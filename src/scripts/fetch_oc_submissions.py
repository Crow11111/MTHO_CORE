"""
Liest Einreichungen von OC für den Osmium Rat (OC → ATLAS).

OC (oder ein Agent auf OC) legt JSON-Dateien in
/var/lib/openclaw/workspace/rat_submissions/ ab. Dieses Skript verbindet per SSH,
liest die Dateien, speichert sie lokal unter data/rat_submissions/ und verschiebt
sie auf dem VPS in ein Archiv (rat_submissions_archive/), damit sie nicht doppelt
gelesen werden.

Schema einer Einreichung (JSON):
  { "from": "oc", "type": "rat_submission"|"info"|"question",
    "created": "ISO8601", "payload": { "topic": "...", "body": "...", ... } }

.env: VPS_HOST, VPS_USER, VPS_PASSWORD.

Aufruf:
  python -m src.scripts.fetch_oc_submissions
  python -m src.scripts.fetch_oc_submissions --dry-run   # nur anzeigen, nichts verschieben
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

HOST = os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
REMOTE_DIR = "/var/lib/openclaw/workspace/rat_submissions"
REMOTE_ARCHIVE = "/var/lib/openclaw/workspace/rat_submissions_archive"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
LOCAL_DIR = os.path.join(PROJECT_ROOT, "data", "rat_submissions")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    os.makedirs(LOCAL_DIR, exist_ok=True)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
    except Exception as e:
        print(f"SSH-Fehler: {e}")
        return 1

    try:
        sftp = ssh.open_sftp()
        try:
            files = sftp.listdir(REMOTE_DIR)
        except FileNotFoundError:
            files = []
        json_files = [f for f in files if f.endswith(".json")]

        if not json_files:
            print("Keine neuen Einreichungen von OC.")
            return 0

        # Archiv auf VPS anlegen
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_ARCHIVE} && chown 1000:1000 {REMOTE_ARCHIVE}")
        stdout.channel.recv_exit_status()

        for name in sorted(json_files):
            remote_path = f"{REMOTE_DIR}/{name}"
            try:
                with sftp.open(remote_path, "r") as f:
                    content = f.read().decode("utf-8")
            except Exception as e:
                print(f"  {name}: Lesefehler – {e}")
                continue
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                data = {"raw": content, "parse_error": True}

            # Lokal speichern
            local_path = os.path.join(LOCAL_DIR, name)
            if not dry_run:
                with open(local_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  {name} -> {local_path}")

            # Auf VPS ins Archiv verschieben
            if not dry_run:
                archive_path = f"{REMOTE_ARCHIVE}/{name}"
                ssh.exec_command(f"mv '{remote_path}' '{archive_path}'")

        sftp.close()
        if dry_run:
            print("(Dry-Run: nichts geschrieben/verschoben)")
        else:
            print(f"{len(json_files)} Einreichung(en) gelesen und nach data/rat_submissions/ übernommen.")
    finally:
        ssh.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
