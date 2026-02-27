"""
Liest die OpenClaw-Config vom VPS (per SSH), prüft JSON und typische Schema-Probleme.
Hinweise für: "Unsupported schema node", Modell-Wechsel speichert nicht, API-Quota-Warnung.

Aufruf: python -m src.scripts.check_openclaw_config_vps
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

CONFIG_PATH = "/var/lib/openclaw/openclaw.json"


def _run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


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

    code, raw, err = _run(ssh, f"cat {CONFIG_PATH} 2>/dev/null || echo ''")
    if not raw or raw.strip() in ("", "{}"):
        code2, out, _ = _run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1")
        if code2 == 0 and out.strip():
            container = out.strip()
            code, raw, err = _run(ssh, f"docker exec {container} cat /home/node/.openclaw/openclaw.json 2>/dev/null || echo ''")
            if raw:
                print(f"Config aus Container {container} gelesen.\n")
    ssh.close()

    if not (raw and raw.strip()):
        print(f"Config nicht lesbar (Host {CONFIG_PATH} oder aus Container).")
        if err:
            print(err)
        return 1

    # JSON parsen
    try:
        cfg = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON-Fehler in openclaw.json: {e}")
        print("Erste 500 Zeichen:", raw[:500])
        return 1

    print("OK: openclaw.json ist gültiges JSON.\n")
    issues = []

    # Typische Ursachen für "Unsupported schema node" / GUI speichert nicht
    if "browser" in cfg and isinstance(cfg["browser"], dict):
        browser = cfg["browser"]
        if "imageModel" in browser:
            issues.append(
                "browser.imageModel: Kann 'Unsupported schema node' in der GUI auslösen. "
                "Lösung: In Raw-Mode bearbeiten oder Key entfernen/umbenennen, falls nicht in der Schema-Doku."
            )
        if "defaultProfile" in browser:
            print(f"  browser.defaultProfile = {browser['defaultProfile']!r}")

    # Leere Strings in Arrays können Probleme machen
    for path, label in [
        ("channels.whatsapp.capabilities", "channels.whatsapp.capabilities"),
        ("skills.allowBundled", "skills.allowBundled"),
    ]:
        parts = path.split(".")
        obj = cfg
        for p in parts[:-1]:
            obj = obj.get(p) if isinstance(obj, dict) else None
            if obj is None:
                break
        if obj is not None and isinstance(obj, dict):
            key = parts[-1]
            val = obj.get(key)
            if isinstance(val, list) and "" in val:
                issues.append(
                    f"{path}: Enthält leeren String ''. Besser: [] oder echte Werte. Kann GUI/Schema stören."
                )

    # agents.list[].model prüfen
    agents_list = (cfg.get("agents") or {}).get("list") or []
    if isinstance(agents_list, list):
        for i, a in enumerate(agents_list):
            if isinstance(a, dict) and "model" in a:
                print(f"  agents.list[{i}].model = {a.get('model')!r}")

    # providers: google vorhanden?
    providers = (cfg.get("models") or {}).get("providers") or {}
    if "google" not in providers and any(
        str((a.get("model") or "")).startswith("google/") for a in agents_list if isinstance(a, dict)
    ):
        issues.append(
            "agents.list verwendet google/..., aber models.providers.google fehlt. "
            "Model-Wechsel auf Gemini wird nicht funktionieren."
        )
    if "google" in providers:
        print("  models.providers.google: vorhanden")

    if not agents_list:
        issues.append(
            "agents.list ist LEER auf dem Server. Ohne Einträge kann die GUI kein Modell zuweisen – "
            "Modell-Wechsel speichert nichts. Config per Raw-Mode oder Datei mit mindestens einem Agent (z.B. id: main, model: google/gemini-3.1-pro-preview) ergänzen."
        )

    def _find_key(d, key, path=""):
        if isinstance(d, dict):
            if key in d:
                yield (path or key, d[key])
            for k, v in d.items():
                yield from _find_key(v, key, f"{path}.{k}" if path else k)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                yield from _find_key(v, key, f"{path}[{i}]")

    for p, v in _find_key(cfg, "imageModel"):
        issues.append(f"Gefunden: {p} = {v!r} – kann 'Unsupported schema node' (Image Model) in der GUI auslösen.")

    # Ausgabe
    if issues:
        print("\n--- Mögliche Ursachen für GUI/Modell-Probleme ---")
        for i, t in enumerate(issues, 1):
            print(f"  {i}. {t}")
    else:
        print("\nKeine offensichtlichen Schema/Format-Probleme gefunden.")
        print("Falls die GUI weiter 'Unsupported schema node' zeigt: OpenClaw Docs prüfen (Image Model, Raw mode).")

    print("\n--- Kurzauszug (meta, agents.defaults.model, agents.list) ---")
    meta = cfg.get("meta") or {}
    print(f"  meta: {meta}")
    defs = (cfg.get("agents") or {}).get("defaults") or {}
    print(f"  agents.defaults.model: {defs.get('model')}")
    print(f"  agents.list: {agents_list}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
