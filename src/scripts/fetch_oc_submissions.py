# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Liest Einreichungen von OC für den Osmium Rat (OC → CORE).

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

load_dotenv("c:/CORE/.env")

HOST = os.getenv("OPENCLAW_ADMIN_VPS_HOST", "").strip() or os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
# Full-Stack VPS: /opt/core-core/openclaw-admin/data/workspace/rat_submissions
REMOTE_DIR = os.getenv("OPENCLAW_RAT_SUBMISSIONS_DIR", "").strip() or "/opt/core-core/openclaw-admin/data/workspace/rat_submissions"
REMOTE_ARCHIVE = (os.getenv("OPENCLAW_RAT_SUBMISSIONS_ARCHIVE", "").strip()
    or (os.path.dirname(REMOTE_DIR) + "/rat_submissions_archive"))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
LOCAL_DIR = os.path.join(PROJECT_ROOT, "data", "rat_submissions")


def run_fetch(dry_run: bool = False, project_root: str | None = None) -> tuple[bool, int, list[dict]]:
    """
    Liest Einreichungen von OC (SSH → VPS), speichert lokal, archiviert auf VPS.
    Zur Nutzung aus API oder Skript.
    Returns: (success, count, items) – items = Liste mit {"file": name, "topic": ... aus payload}
    """
    root = project_root or PROJECT_ROOT
    local_dir = os.path.join(root, "data", "rat_submissions")
    if not HOST or not USER:
        return False, 0, []

    os.makedirs(local_dir, exist_ok=True)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY_PATH and os.path.isfile(KEY_PATH):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
    except Exception:
        return False, 0, []

    items: list[dict] = []
    try:
        sftp = ssh.open_sftp()
        try:
            files = sftp.listdir(REMOTE_DIR)
        except FileNotFoundError:
            files = []
        json_files = [f for f in files if f.endswith(".json")]

        if not json_files:
            return True, 0, []

        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_ARCHIVE} && chown 1000:1000 {REMOTE_ARCHIVE}")
        stdout.channel.recv_exit_status()

        for name in sorted(json_files):
            remote_path = f"{REMOTE_DIR}/{name}"
            try:
                with sftp.open(remote_path, "r") as f:
                    content = f.read().decode("utf-8")
            except Exception:
                continue
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                data = {"raw": content[:200], "parse_error": True}

            payload = data.get("payload") or {}
            topic = payload.get("topic", data.get("type", ""))
            items.append({"file": name, "topic": str(topic)[:200]})

            local_path = os.path.join(local_dir, name)
            if not dry_run:
                with open(local_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            if not dry_run:
                archive_path = f"{REMOTE_ARCHIVE}/{name}"
                ssh.exec_command(f"mv '{remote_path}' '{archive_path}'")

        sftp.close()
    finally:
        ssh.close()

    return True, len(items), items


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    ok, count, items = run_fetch(dry_run=dry_run)
    if not ok:
        print("SSH-Fehler oder Konfiguration fehlt.")
        return 1
    if count == 0:
        print("Keine neuen Einreichungen von OC.")
        return 0
    for it in items:
        print(f"  {it['file']} -> data/rat_submissions/")
    if dry_run:
        print("(Dry-Run: nichts geschrieben/verschoben)")
    else:
        print(f"{count} Einreichung(en) gelesen und nach data/rat_submissions/ übernommen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
