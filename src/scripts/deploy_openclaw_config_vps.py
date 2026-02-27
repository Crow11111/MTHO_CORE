"""
Liest openclaw.json vom VPS, behebt bekannte GUI-Probleme, schreibt zurück.

Behobene Punkte:
- "Unsupported schema node" (Image Model): imageModel-Keys werden entfernt.
- Modell-Auswahl speichert nicht: agents.list und agents.defaults werden gesetzt.
- Leere Strings in Arrays: channels.whatsapp.capabilities, skills.allowBundled → [].

.env: VPS_HOST, VPS_USER, VPS_PASSWORD, OPENCLAW_GATEWAY_TOKEN

Aufruf:
  python -m src.scripts.deploy_openclaw_config_vps
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("VPS_HOST", "").strip()
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN", "") or "").strip().strip('"')

CONFIG_PATH_HOST = "/var/lib/openclaw/openclaw.json"


def _run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


def _remove_image_model(obj):
    """Entfernt alle Keys 'imageModel' rekursiv – behebt Schema-Warnung 'Unsupported schema node' (Image Model)."""
    if isinstance(obj, dict):
        obj.pop("imageModel", None)
        for v in obj.values():
            _remove_image_model(v)
    elif isinstance(obj, list):
        for v in obj:
            _remove_image_model(v)
    return obj


def _fix_empty_arrays(cfg: dict) -> None:
    """Leere Strings in Arrays ersetzen (capabilities, allowBundled)."""
    w = (cfg.get("channels") or {}).get("whatsapp")
    if isinstance(w, dict) and isinstance(w.get("capabilities"), list) and "" in w["capabilities"]:
        w["capabilities"] = [x for x in w["capabilities"] if x != ""] or []
    s = cfg.get("skills")
    if isinstance(s, dict) and isinstance(s.get("allowBundled"), list) and "" in s["allowBundled"]:
        s["allowBundled"] = [x for x in s["allowBundled"] if x != ""] or []


# Gemini als Standardmodell für OC (main-Agent)
GEMINI_MODEL_ID = "google/gemini-3.1-pro-preview"
GEMINI_ALIAS = "Gemini 3.1 Pro"


def _ensure_agents(cfg: dict) -> None:
    """Stellt agents.list (main + Agent) und agents.defaults sicher. Bestehendes Modell wird nicht überschrieben."""
    if "agents" not in cfg:
        cfg["agents"] = {}
    agents = cfg["agents"]
    if not isinstance(agents.get("list"), list) or len(agents["list"]) == 0:
        agents["list"] = [
            {"id": "main", "name": "main", "model": GEMINI_MODEL_ID},
            {"id": "agent", "name": "Agent", "model": GEMINI_MODEL_ID},
        ]
    else:
        # Zweiten Agenten "agent" (Name: Agent) hinzufügen, falls noch nicht vorhanden
        ids = {a.get("id") for a in agents["list"] if isinstance(a, dict)}
        if "agent" not in ids:
            main_model = GEMINI_MODEL_ID
            for a in agents["list"]:
                if isinstance(a, dict) and a.get("id") == "main":
                    main_model = a.get("model") or GEMINI_MODEL_ID
                    break
            agents["list"].append({"id": "agent", "name": "Agent", "model": main_model})
            print("  Zweiten Agenten 'agent' (Name: Agent) hinzugefügt.")
    if "defaults" not in agents:
        agents["defaults"] = {}
    defaults = agents["defaults"]
    if not isinstance(defaults.get("model"), dict):
        defaults["model"] = {}
    # primary nur setzen wenn noch nicht gesetzt
    if not defaults["model"].get("primary"):
        defaults["model"]["primary"] = GEMINI_ALIAS
    if "models" not in defaults or not isinstance(defaults["models"], dict):
        defaults["models"] = {}
    defaults["models"][GEMINI_MODEL_ID] = {"alias": GEMINI_ALIAS}


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    print(f"Verbinde mit {USER}@{HOST} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY_PATH and os.path.isfile(KEY_PATH):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
    except Exception as e:
        print(f"SSH-Fehler: {e}")
        return 1

    # Config lesen (Host oder aus Container)
    code, raw, _ = _run(ssh, f"cat {CONFIG_PATH_HOST} 2>/dev/null || echo ''")
    if not raw or raw.strip() in ("", "{}"):
        code2, out, _ = _run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1")
        if out.strip():
            container = out.strip()
            code, raw, _ = _run(ssh, f"docker exec {container} cat /home/node/.openclaw/openclaw.json 2>/dev/null || echo ''")
            if raw:
                print(f"Config aus Container {container} gelesen.")

    if not (raw and raw.strip()):
        print("FEHLER: openclaw.json weder auf Host noch im Container lesbar.")
        ssh.close()
        return 1

    try:
        cfg = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FEHLER: openclaw.json ist kein gültiges JSON: {e}")
        ssh.close()
        return 1

    # 1) imageModel entfernen → Schema-Warnung "Unsupported schema node" (Image Model) weg
    _remove_image_model(cfg)
    print("  imageModel entfernt (Schema-Warnung behoben).")

    # 2) Leere Arrays bereinigen
    _fix_empty_arrays(cfg)
    print("  capabilities / allowBundled bereinigt.")

    # 3) agents.list und agents.defaults setzen
    _ensure_agents(cfg)
    print("  agents.list und agents.defaults gesetzt.")

    # Provider Google hinzufügen
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
    if GEMINI_API_KEY:
        if "models" not in cfg:
            cfg["models"] = {}
        if "providers" not in cfg["models"]:
            cfg["models"]["providers"] = {}
        cfg["models"]["providers"]["google"] = {
            "apiKey": GEMINI_API_KEY
        }
        print("  Provider 'google' mit GEMINI_API_KEY hinzugefügt.")
    else:
        print("  WARNUNG: GEMINI_API_KEY nicht in .env gefunden. Provider 'google' konnte nicht gesetzt werden.")

    # 4) Gateway: Token und Endpoints (Chat/UI verbindet sich mit Gateway)
    if "gateway" not in cfg:
        cfg["gateway"] = {}
    g = cfg["gateway"]
    if TOKEN:
        g["auth"] = {"mode": "token", "token": TOKEN}
        g["remote"] = {"token": TOKEN}
        if "hooks" not in cfg:
            cfg["hooks"] = {}
        cfg["hooks"]["token"] = TOKEN
    # Damit Gateway-UI und externe Aufrufe funktionieren
    if "http" not in g:
        g["http"] = {}
    if "endpoints" not in g["http"]:
        g["http"]["endpoints"] = {}
    g["http"]["endpoints"]["responses"] = {"enabled": True}
    # controlUi: oft nötig für Dashboard/Chat-Verbindung
    if "controlUi" not in g:
        g["controlUi"] = {
            "dangerouslyAllowHostHeaderOriginFallback": True,
            "allowInsecureAuth": True,
            "dangerouslyDisableDeviceAuth": True,
        }

    merged = json.dumps(cfg, indent=2, ensure_ascii=False)
    b64 = __import__("base64").standard_b64encode(merged.encode("utf-8")).decode("ascii")

    # Auf Host schreiben (Container liest gemountete Datei)
    _run(ssh, f"mkdir -p /var/lib/openclaw")
    _run(ssh, f"echo '{b64}' | base64 -d > {CONFIG_PATH_HOST} && chmod 644 {CONFIG_PATH_HOST}")
    _run(ssh, "chown -R 1000:1000 /var/lib/openclaw 2>/dev/null || true")
    print(f"  Config nach {CONFIG_PATH_HOST} geschrieben.")

    # Session-Locks entfernen, dann Container neu starten
    code, out, _ = _run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' || true")
    for c in (out or "").strip().splitlines():
        c = c.strip()
        if c:
            _run(ssh, f"docker exec {c} sh -c 'rm -f /data/.openclaw/agents/main/sessions/*.lock 2>/dev/null'")
            print("  Session-Locks bereinigt.")
            _run(ssh, f"docker restart {c}")
            print(f"  Container {c} neugestartet.")
            break

    ssh.close()
    print("Fertig. GUI: Schema-Warnung (Image Model) sollte weg sein, Modell-Auswahl sollte speichern.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
