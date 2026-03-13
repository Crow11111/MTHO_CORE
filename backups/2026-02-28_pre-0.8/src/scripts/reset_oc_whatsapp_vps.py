"""
WhatsApp-Session auf OpenClaw-VPS zurücksetzen („Gerät konnte nicht hinzugefügt werden“).

Löscht credentials/whatsapp im OpenClaw-Admin-Volume und startet den Container neu.
Danach in der Control-UI unter Channels → WhatsApp erneut pairen (neuer QR/Pairing-Code).

.env: OPENCLAW_ADMIN_VPS_HOST (oder VPS_HOST), VPS_USER, VPS_PASSWORD/SSH_KEY.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

ADMIN_HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST", "")).strip()
ADMIN_USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER", "root")).strip()
ADMIN_PASS = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD", "")).strip()
ADMIN_KEY = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY", "")).strip()
ADMIN_PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT", "22"))

# Full-Stack: Volume auf Host
BASE_DATA = "/opt/atlas-core/openclaw-admin/data"
CREDENTIALS_WHATSAPP = f"{BASE_DATA}/credentials/whatsapp"


def run(ssh, cmd):
    c = ssh.get_transport().open_session()
    c.exec_command(cmd)
    out = c.recv(65535).decode("utf-8", errors="replace").strip()
    err = c.recv_stderr(65535).decode("utf-8", errors="replace").strip()
    code = c.recv_exit_status()
    return code, out, err


def main():
    if not ADMIN_HOST or not ADMIN_USER:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST bzw. VPS_USER in .env fehlt.")
        return 1
    print(f"[SSH] {ADMIN_USER}@{ADMIN_HOST}:{ADMIN_PORT} …")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if ADMIN_KEY and os.path.isfile(ADMIN_KEY):
            ssh.connect(ADMIN_HOST, port=ADMIN_PORT, username=ADMIN_USER, key_filename=ADMIN_KEY, timeout=15)
        else:
            ssh.connect(ADMIN_HOST, port=ADMIN_PORT, username=ADMIN_USER, password=ADMIN_PASS or None, timeout=15)
    except Exception as e:
        print(f"  SSH-Fehler: {e}")
        return 1
    print("  OK")

    # 1) WhatsApp-Credentials löschen (Host-Pfad, da Volume gemountet)
    print("  Lösche WhatsApp-Session (credentials/whatsapp) …")
    code, out, err = run(ssh, f"rm -rf {CREDENTIALS_WHATSAPP} && echo GELOESCHT || echo FEHLER")
    if "GELOESCHT" in out:
        print("    credentials/whatsapp entfernt.")
    else:
        print(f"    Ausgabe: {out or err or '(kein)'}")

    # 2) Container neu starten
    print("  Starte openclaw-admin neu …")
    code, out, err = run(ssh, "cd /opt/atlas-core && docker compose restart openclaw-admin 2>&1")
    if code != 0:
        print(f"    Warnung: {err or out}")
    else:
        print("    Container neu gestartet.")

    ssh.close()
    print("\nFertig. In der Control-UI (Channels > WhatsApp) erneut pairen - neuer QR oder Pairing-Code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
