# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

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

# Am Admin-VPS (deploy_vps_full_stack): Config unter /opt/core-core/openclaw-admin/data/
CONFIG_PATH_HOST = os.getenv("OPENCLAW_CONFIG_PATH", "").strip() or "/var/lib/openclaw/openclaw.json"
CONFIG_PATH_FULLSTACK = "/opt/core-core/openclaw-admin/data/openclaw.json"


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


# Gemini als Standardmodell für OC (main-Agent). primary/defaults.model.primary = Modell-ID (provider/id), nicht Alias.
GEMINI_MODEL_ID = "google/gemini-3.1-pro-preview"

# Vollständige Modelllisten (Schema: models.providers.<provider>.models = Array von {id, name})
GOOGLE_MODELS = [
    {"id": "gemini-3.1-pro-preview", "name": "Gemini 3.1 Pro"},
    {"id": "gemini-3-pro-preview", "name": "Gemini 3 Pro"},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
    {"id": "gemini-3.1-flash-preview", "name": "Gemini 3.1 Flash"},
    {"id": "gemini-3-flash-preview", "name": "Gemini 3 Flash"},
    {"id": "deep-research-pro-preview-12-2025", "name": "Gemini Deep Research"},
]
ANTHROPIC_MODELS = [
    {"id": "claude-opus-4-6", "name": "Claude Opus 4.6"},
    {"id": "claude-opus-4-5", "name": "Claude Opus 4.5"},
    {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
    {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5"},
]


def _defaults_models_catalog() -> dict:
    """agents.defaults.models: Key = provider/model-id, Value = {alias}. Alle konfigurierten Modelle für UI-Auswahl."""
    out = {}
    for m in GOOGLE_MODELS:
        out["google/" + m["id"]] = {"alias": m["name"]}
    for m in ANTHROPIC_MODELS:
        out["anthropic/" + m["id"]] = {"alias": m["name"]}
    return out


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
    if not isinstance(defaults.get("workspace"), str) or not defaults.get("workspace"):
        defaults["workspace"] = "/home/node/.openclaw/workspace"
    if not isinstance(defaults.get("model"), dict):
        defaults["model"] = {}
    # primary = Modell-ID (provider/id), nicht Alias – Schema: "Primary model ID to use"
    primary = defaults["model"].get("primary")
    if not primary or "/" not in str(primary):
        defaults["model"]["primary"] = GEMINI_MODEL_ID
    # defaults.models: alle konfigurierten Modelle mit Alias, damit UI alle anzeigen kann
    if "models" not in defaults or not isinstance(defaults["models"], dict):
        defaults["models"] = {}
    for mid, entry in _defaults_models_catalog().items():
        defaults["models"][mid] = entry


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

    # Config lesen: Host (priorisiere Full-Stack-Pfad wenn vorhanden) oder aus Container
    write_path = CONFIG_PATH_HOST
    read_path = CONFIG_PATH_HOST
    if CONFIG_PATH_HOST == "/var/lib/openclaw/openclaw.json":
        c_check, out_check, _ = _run(ssh, f"cat {CONFIG_PATH_FULLSTACK} 2>/dev/null || echo ''")
        if out_check and out_check.strip() and out_check.strip() != "{}":
            read_path = write_path = CONFIG_PATH_FULLSTACK
            raw = out_check
        else:
            raw = ""
    if not raw or raw.strip() in ("", "{}"):
        code, raw, _ = _run(ssh, f"cat {read_path} 2>/dev/null || echo ''")
    if not raw or raw.strip() in ("", "{}"):
        code2, out, _ = _run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1")
        if out.strip():
            container = out.strip()
            code, raw, _ = _run(ssh, f"docker exec {container} cat /home/node/.openclaw/openclaw.json 2>/dev/null || echo ''")
            if raw:
                print(f"Config aus Container {container} gelesen.")
                write_path = CONFIG_PATH_FULLSTACK

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

    # 0) Platzhalter durch echte Env-Werte ersetzen (invalid config wegen REDACTED/$VAR vermeiden)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip().strip('"')
    for key in ("apiKey", "token"):
        for provider_key in ("google", "anthropic"):
            p = (cfg.get("models") or {}).get("providers") or {}
            if provider_key in p and isinstance(p[provider_key], dict):
                val = p[provider_key].get(key)
                if isinstance(val, str) and ("REDACTED" in val or val.strip().startswith("$")):
                    if provider_key == "google" and GEMINI_API_KEY:
                        p[provider_key][key] = GEMINI_API_KEY
                        print(f"  Platzhalter in models.providers.{provider_key}.{key} durch .env ersetzt.")
                    elif provider_key == "anthropic" and ANTHROPIC_KEY:
                        p[provider_key][key] = ANTHROPIC_KEY
                        print(f"  Platzhalter in models.providers.{provider_key}.{key} durch .env ersetzt.")
    if cfg.get("gateway") and TOKEN:
        for section in ("auth", "remote"):
            g = cfg["gateway"].get(section)
            if isinstance(g, dict) and g.get("token") and ("REDACTED" in str(g.get("token")) or str(g.get("token")).strip().startswith("$")):
                cfg["gateway"][section]["token"] = TOKEN
                print(f"  Platzhalter in gateway.{section}.token durch .env ersetzt.")

    # 1) imageModel entfernen → Schema-Warnung "Unsupported schema node" (Image Model) weg
    _remove_image_model(cfg)
    print("  imageModel entfernt (Schema-Warnung behoben).")

    # 2) Leere Arrays bereinigen
    _fix_empty_arrays(cfg)
    print("  capabilities / allowBundled bereinigt.")

    # 3) agents.list und agents.defaults setzen
    _ensure_agents(cfg)
    print("  agents.list und agents.defaults gesetzt.")

    # Provider Google hinzufügen (baseUrl + models nicht überschreiben falls vorhanden)
    if GEMINI_API_KEY:
        if "models" not in cfg:
            cfg["models"] = {}
        if "providers" not in cfg["models"]:
            cfg["models"]["providers"] = {}
        g = cfg["models"]["providers"].setdefault("google", {})
        g["apiKey"] = GEMINI_API_KEY
        g.setdefault("baseUrl", "https://generativelanguage.googleapis.com/v1beta/")
        if "models" not in g or not g["models"]:
            g["models"] = list(GOOGLE_MODELS)
        print("  Provider 'google' mit GEMINI_API_KEY und Modellliste gesetzt.")
    else:
        print("  WARNUNG: GEMINI_API_KEY nicht in .env gefunden. Provider 'google' konnte nicht gesetzt werden.")

    # Provider Anthropic (Key aus .env, Modellliste falls fehlend)
    if ANTHROPIC_KEY:
        if "models" not in cfg:
            cfg["models"] = {}
        if "providers" not in cfg["models"]:
            cfg["models"]["providers"] = {}
        a = cfg["models"]["providers"].setdefault("anthropic", {})
        a["apiKey"] = ANTHROPIC_KEY
        a.setdefault("baseUrl", "https://api.anthropic.com/v1")
        a.setdefault("api", "anthropic-messages")
        if "models" not in a or not a["models"]:
            a["models"] = list(ANTHROPIC_MODELS)
        print("  Provider 'anthropic' mit ANTHROPIC_API_KEY und Modellliste gesetzt.")

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
    dir_oc = os.path.dirname(write_path)
    _run(ssh, f"mkdir -p {dir_oc}")
    _run(ssh, f"echo '{b64}' | base64 -d > {write_path} && chmod 644 {write_path}")
    _run(ssh, f"chown -R 1000:1000 {dir_oc} 2>/dev/null || true")
    print(f"  Config nach {write_path} geschrieben.")

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
