# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Führt auf dem VPS im OpenClaw-Container 'openclaw doctor' aus.
Gibt den exakten Schema-/Validierungsfehler aus (Pfad des fehlerhaften Felds).

.env: VPS_HOST, VPS_USER, VPS_PASSWORD oder VPS_SSH_KEY

Aufruf: python -m src.scripts.openclaw_doctor_vps
"""
from __future__ import annotations

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

    # Container finden
    code, out, _ = _run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1")
    container = (out or "").strip()
    if not container:
        print("Kein OpenClaw-Container gefunden (docker ps | grep openclaw).")
        ssh.close()
        return 1

    print(f"Container: {container}")
    print("--- openclaw doctor ---")
    code, out, err = _run(ssh, f"docker exec {container} openclaw doctor 2>&1")
    text = (out or err or "(keine Ausgabe)")
    # Windows-Konsole (cp1252) kann Unicode aus openclaw doctor nicht darstellen
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))
    if code != 0:
        print(f"Exit-Code: {code}")
    ssh.close()
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
