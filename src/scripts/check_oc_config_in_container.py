"""
Prüft von außen (per SSH), was der OpenClaw-Container innen unter dem Config-Mount sieht.
Zeigt: ls /home/node/.openclaw und Inhalt von openclaw.json (falls vorhanden).

Aufruf: python -m src.scripts.check_oc_config_in_container
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


def run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() + stderr.read()).decode("utf-8", errors="replace").strip()
    return code, out


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

    # Container-Name finden (Hostinger oder unser)
    code, out = run(ssh, "docker ps --format '{{.Names}}' | grep -E 'openclaw|hvps' || true")
    containers = [n.strip() for n in out.splitlines() if n.strip()]
    if not containers:
        print("Kein OpenClaw-Container gefunden.")
        ssh.close()
        return 1

    # Ersten nehmen (Hostinger oft openclaw-ntw5-openclaw-1)
    container = containers[0]
    print(f"Container: {container}\n")

    # Was sieht der Container unter dem Config-Pfad?
    code, out = run(ssh, f"docker exec {container} ls -la /home/node/.openclaw 2>&1")
    print("--- ls /home/node/.openclaw ---")
    print(out or "(leer oder Pfad existiert nicht)")
    print()

    code, out = run(ssh, f"docker exec {container} cat /home/node/.openclaw/openclaw.json 2>&1")
    print("--- openclaw.json (Auszug) ---")
    if out and "No such file" not in out:
        print(out[:2000] + ("..." if len(out) > 2000 else ""))
        if "responses" in out and "enabled" in out:
            print("\n-> responses/enabled ist in der Datei erwähnt.")
    else:
        print(out or "(Datei nicht lesbar)")
    ssh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
