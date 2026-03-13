# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Behebt zwei Probleme auf dem VPS per SSH:
1. Stale session lock file entfernen (blockiert alle Modelle)
2. auth-profiles.json mit GEMINI_API_KEY anlegen (No API key for google)

Aufruf: python -m src.scripts.fix_openclaw_lock_and_auth
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

LOCK_FILE = "/data/.openclaw/agents/main/sessions/47ebc8c5-6854-430e-83d9-6c2e30efbc3d.jsonl.lock"
AUTH_DIR = "/data/.openclaw/agents/main/agent"
AUTH_FILE = f"{AUTH_DIR}/auth-profiles.json"


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

    # Container-Name finden
    code, out, _ = _run(ssh, "docker ps --format '{{.Names}}' | grep -iE 'openclaw' | head -1")
    container = out.strip()
    if not container:
        print("FEHLER: Kein OpenClaw-Container gefunden.")
        ssh.close()
        return 1
    print(f"Container: {container}")

    # 1. Stale lock file entfernen
    print(f"\n[1/3] Stale lock file entfernen...")
    code, out, err = _run(ssh, f"docker exec {container} rm -f {LOCK_FILE}")
    print(f"      {'OK' if code == 0 else 'Fehler: ' + err}")

    # 2. auth-profiles.json mit Google-Key anlegen
    print(f"\n[2/3] auth-profiles.json mit GEMINI_API_KEY setzen...")
    auth = {"google": {"apiKey": GEMINI_KEY}}
    auth_json = json.dumps(auth, indent=2)
    b64 = base64.standard_b64encode(auth_json.encode("utf-8")).decode("ascii")
    _run(ssh, f"docker exec {container} mkdir -p {AUTH_DIR}")
    code, out, err = _run(ssh, f"docker exec {container} sh -c 'echo {b64} | base64 -d > {AUTH_FILE}'")
    if code == 0:
        code2, content, _ = _run(ssh, f"docker exec {container} cat {AUTH_FILE}")
        print(f"      OK. Inhalt: {content[:100]}")
    else:
        print(f"      Fehler: {err}")
        ssh.close()
        return 1

    # 3. Container neu starten
    print(f"\n[3/3] Container {container} neu starten...")
    code, out, err = _run(ssh, f"docker restart {container}")
    print(f"      {'OK: ' + out if code == 0 else 'Fehler: ' + err}")

    ssh.close()
    print("\nFertig. 10-15s warten, dann OpenClaw-GUI neu laden und testen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
