"""
Stammdokumente für OC auf den Hostinger-VPS deployen.

Liest alle .md-Dateien aus docs/stammdokumente_oc/ und legt sie auf dem VPS
unter /var/lib/openclaw/workspace/stammdokumente/ ab (für OC einsehbar).

Nur ausführen nach Freigabe durch den Rat (Osmium Council).
.env: VPS_HOST, VPS_USER, VPS_PASSWORD.

Aufruf (aus Projekt-Root):
  python -m src.scripts.deploy_stammdokumente_vps
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

HOST = os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
REMOTE_DIR = "/var/lib/openclaw/workspace/stammdokumente"

# Projekt-Root: von src/scripts zwei Ebenen hoch
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
LOCAL_DIR = os.path.join(PROJECT_ROOT, "docs", "01_CORE_DNA", "stammdokumente_oc")


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1
    if not os.path.isdir(LOCAL_DIR):
        print(f"FEHLER: Lokaler Ordner nicht gefunden: {LOCAL_DIR}")
        return 1

    md_files = [f for f in os.listdir(LOCAL_DIR) if f.endswith(".md")]
    if not md_files:
        print(f"Keine .md-Dateien in {LOCAL_DIR}")
        return 0

    print(f"Verbinde mit {USER}@{HOST}:{PORT} ...")
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

    try:
        sftp = ssh.open_sftp()
        # Remote-Verzeichnis anlegen (als root; chown danach)
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_DIR} && chown -R 1000:1000 {REMOTE_DIR}")
        stdout.channel.recv_exit_status()
        if stderr.channel.recv_stderr(4096):
            pass  # ggf. schon vorhanden

        for name in sorted(md_files):
            local_path = os.path.join(LOCAL_DIR, name)
            remote_path = f"{REMOTE_DIR}/{name}"
            sftp.put(local_path, remote_path)
            print(f"  {name} -> {remote_path}")
        sftp.close()

        # Rechte für OC-Container-User (1000:1000)
        stdin, stdout, stderr = ssh.exec_command(f"chown -R 1000:1000 {REMOTE_DIR} && chmod -R 644 {REMOTE_DIR} && chmod 755 {REMOTE_DIR}")
        stdout.channel.recv_exit_status()
        print(f"Stammdokumente abgelegt unter {REMOTE_DIR} (für OC einsehbar).")
        print("Nächster Schritt: OC per WhatsApp informieren (siehe docs/04_PROCESSES/STAMMDOKUMENTE_DEPLOY.md).")
    finally:
        ssh.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
