"""
Fixiert OpenClaw im richtigen Pfad /data/.openclaw/ (Hostinger-Container):
1. auth-profiles.json: Google-Key im korrekten Format hinzufügen
2. openclaw.json: google-Provider + agents.list mit google/gemini-3.1-pro-preview
3. Container neustarten

Aufruf: python -m src.scripts.fix_openclaw_data_path
"""
from __future__ import annotations

import base64
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
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')

CONTAINER = "openclaw-ntw5-openclaw-1"
DATA_ROOT = "/data/.openclaw"
AUTH_FILE = f"{DATA_ROOT}/agents/main/agent/auth-profiles.json"
CFG_FILE  = f"{DATA_ROOT}/openclaw.json"


def _run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


def write_json_to_container(ssh: paramiko.SSHClient, container: str, path: str, data: dict) -> bool:
    payload = json.dumps(data, indent=2)
    b64 = base64.standard_b64encode(payload.encode("utf-8")).decode("ascii")
    code, out, err = _run(ssh, f"docker exec {container} sh -c 'echo {b64} | base64 -d > {path}'")
    return code == 0


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1
    if not GEMINI_KEY:
        print("FEHLER: GEMINI_API_KEY in .env fehlt.")
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

    # --- 1. auth-profiles.json ---
    print(f"\n[1/3] auth-profiles.json patchen ({AUTH_FILE})...")
    code, raw, _ = _run(ssh, f"docker exec {CONTAINER} cat {AUTH_FILE} 2>/dev/null")
    try:
        auth = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        auth = {}

    # Korrektes Format sicherstellen
    auth.setdefault("version", 1)
    auth.setdefault("profiles", {})
    auth.setdefault("lastGood", {})

    # Google hinzufügen / überschreiben
    auth["profiles"]["google:default"] = {
        "provider": "google",
        "type": "api_key",
        "key": GEMINI_KEY,
    }
    auth["lastGood"]["google"] = "google:default"

    if write_json_to_container(ssh, CONTAINER, AUTH_FILE, auth):
        print("      OK")
    else:
        print("      FEHLER beim Schreiben")
        ssh.close()
        return 1

    # --- 2. openclaw.json: google-Provider + agents.list ---
    print(f"\n[2/3] openclaw.json patchen ({CFG_FILE})...")
    code, raw2, _ = _run(ssh, f"docker exec {CONTAINER} cat {CFG_FILE} 2>/dev/null")
    try:
        cfg = json.loads(raw2) if raw2 else {}
    except json.JSONDecodeError:
        cfg = {}

    # Google-Provider eintragen
    cfg.setdefault("models", {}).setdefault("providers", {})
    cfg["models"]["providers"]["google"] = {"apiKey": GEMINI_KEY}

    # agents.defaults.model setzen
    cfg.setdefault("agents", {}).setdefault("defaults", {})
    cfg["agents"]["defaults"]["model"] = {"primary": "google/gemini-3.1-pro-preview"}

    # agents.list: main-Agent auf Gemini setzen
    agents_list = cfg["agents"].get("list") or []
    main_found = False
    for a in agents_list:
        if isinstance(a, dict) and a.get("id") == "main":
            a["model"] = "google/gemini-3.1-pro-preview"
            main_found = True
    if not main_found:
        agents_list.append({"id": "main", "name": "main", "model": "google/gemini-3.1-pro-preview"})
    cfg["agents"]["list"] = agents_list

    if write_json_to_container(ssh, CONTAINER, CFG_FILE, cfg):
        print("      OK")
    else:
        print("      FEHLER beim Schreiben")
        ssh.close()
        return 1

    # --- 3. Container restart ---
    print(f"\n[3/3] Container {CONTAINER} neustarten...")
    code, out, err = _run(ssh, f"docker restart {CONTAINER}")
    print(f"      {'OK: ' + out if code == 0 else 'Fehler: ' + err}")

    # --- Verify ---
    import time
    time.sleep(5)
    code, v, _ = _run(ssh, f"docker exec {CONTAINER} sh -c 'grep -c google {AUTH_FILE} 2>/dev/null'")
    print(f"\nVerifizierung: Google-Einträge in auth-profiles.json: {v}")

    ssh.close()
    print("\nFertig. GUI neu laden und Modell testen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
