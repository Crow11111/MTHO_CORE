"""
Alternative zum API-Trigger: Legt die WhatsApp-Plan-Aufgabe als Datei in OCs Workspace
auf dem VPS ab. Wenn die Gateway-API 405 liefert, kannst du danach per WhatsApp @OC
schreiben: „Lies workspace/whatsapp_plan_task.md und fülle Abschnitt 6 aus; Antwort
in rat_submissions mit topic WhatsApp-Plan Abschnitt 6.“

.env: VPS_HOST, VPS_USER, VPS_PASSWORD (oder VPS_SSH_KEY)

Aufruf:
  python -m src.scripts.deploy_whatsapp_plan_task_to_oc
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

REMOTE_DIR = "/var/lib/openclaw/workspace"
REMOTE_FILE = "whatsapp_plan_task.md"

TASK_CONTENT = """# Aufgabe: WhatsApp-Plan Abschnitt 6 ausfüllen (OC)

Bitte fülle deinen Teil in Abschnitt 6 des Plans aus.

## Deine Punkte

1. **Empfohlenes Procedere** für „nur richtige Absender / unterschiedliche Nummern“ (z. B. allowFrom, getrennte Nummer, Kombination mit @OC).
2. **Siehst du aktuell nur Nachrichten „von Marc an Marc“?** Wie spielt das mit der Trigger-Regel zusammen?

## Antwort

Bitte lege deine Antwort als Einreichung in **rat_submissions/** ab:

- **type:** "info" oder "rat_submission"
- **payload.topic:** "WhatsApp-Plan Abschnitt 6"
- **payload.body:** dein Text (Vorschläge, Procedere, wie du Nachrichten siehst).

ATLAS holt die Einreichungen mit fetch_oc_submissions ab und trägt sie in den Plan ein.
"""


def main() -> int:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

    HOST = os.getenv("VPS_HOST", "").strip()
    PORT = int(os.getenv("VPS_SSH_PORT", "22"))
    USER = os.getenv("VPS_USER", "root")
    PASSWORD = os.getenv("VPS_PASSWORD", "")
    KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()

    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    import paramiko
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
        try:
            sftp.stat(REMOTE_DIR)
        except FileNotFoundError:
            ssh.exec_command(f"mkdir -p {REMOTE_DIR} && chown -R 1000:1000 {REMOTE_DIR}")
        remote_path = f"{REMOTE_DIR}/{REMOTE_FILE}"
        with sftp.file(remote_path, "w") as f:
            f.write(TASK_CONTENT)
        sftp.close()
        ssh.exec_command(f"chown 1000:1000 {remote_path} && chmod 644 {remote_path}")
        print(f"Datei abgelegt: {remote_path}")
        print("Nächster Schritt: Eine WhatsApp-Nachricht, die mit @OC beginnt (reicht völlig):")
        print('  @OC Lies workspace/whatsapp_plan_task.md und fülle Abschnitt 6 aus; Antwort in rat_submissions (topic: WhatsApp-Plan Abschnitt 6).')
    finally:
        ssh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
