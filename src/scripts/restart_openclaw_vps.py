"""
Startet den OpenClaw-Gateway-Container auf dem VPS neu.

Damit die Gateway-Config (z. B. gateway.http.endpoints.responses.enabled: true) greift,
muss der Container einmal neugestartet werden. Danach können test_atlas_oc_channel --send
und send_offene_punkte_to_oc laufen.

.env: VPS_HOST, VPS_USER, VPS_PASSWORD

Aufruf:
  python -m src.scripts.restart_openclaw_vps
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

# .env im Projektroot (bei Aufruf: python -m src.scripts.restart_openclaw_vps)
load_dotenv()

HOST = os.getenv("VPS_HOST", "").strip()
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))


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

    # Container-Name ermitteln (openclaw-gateway oder per grep)
    stdin, stdout, stderr = ssh.exec_command(
        "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1"
    )
    container = (stdout.read().decode("utf-8", errors="replace") or "").strip() or "openclaw-gateway"

    # Session-Lock-Dateien entfernen (behebt "session file locked (timeout)")
    print(f"Entferne Session-Locks in {container} ...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {container} sh -c 'rm -f /data/.openclaw/agents/main/sessions/*.lock 2>/dev/null; echo done'"
    )
    stdout.channel.recv_exit_status()
    print("  Locks bereinigt.")

    print(f"Starte {container} neu (docker restart) ...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {container}")
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    ssh.close()

    if code != 0:
        print(f"Fehler (Exit {code}): {err or out}")
        return 1
    print(out or "Container neugestartet.")
    print("Kurz warten (z. B. 10 s), dann: python -m src.scripts.test_atlas_oc_channel --send")
    return 0


if __name__ == "__main__":
    sys.exit(main())
