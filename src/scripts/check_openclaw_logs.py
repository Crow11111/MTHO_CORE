"""
Zeigt Container-Logs und prüft ob die openclaw.json valides JSON ist.
Aufruf: python -m src.scripts.check_openclaw_logs
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import json, paramiko
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("VPS_HOST","").strip()
USER = os.getenv("VPS_USER","root")
PASSWORD = os.getenv("VPS_PASSWORD","")
KEY_PATH = os.getenv("VPS_SSH_KEY","").strip()
PORT = int(os.getenv("VPS_SSH_PORT","22"))
CONTAINER = "openclaw-ntw5-openclaw-1"

def _run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if KEY_PATH and os.path.isfile(KEY_PATH):
        ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
    else:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)

    print("=== Container Status ===")
    out, _ = _run(ssh, f"docker ps -a --filter name={CONTAINER} --format '{{{{.Names}}}} {{{{.Status}}}}'")
    print(out)

    print("\n=== Letzte 40 Logs ===")
    out, err = _run(ssh, f"docker logs {CONTAINER} --tail 40 2>&1")
    # Nur ASCII ausgeben, Sonderzeichen ersetzen
    safe = (out or err or "(keine Logs)").encode("ascii", errors="replace").decode("ascii")
    print(safe)

    print("\n=== JSON-Validierung (/data/.openclaw/openclaw.json) ===")
    out, _ = _run(ssh, f"docker exec {CONTAINER} cat /data/.openclaw/openclaw.json 2>/dev/null")
    if out:
        try:
            cfg = json.loads(out)
            print("JSON OK")
            agents = (cfg.get("agents") or {}).get("list") or []
            print(f"agents.list: {agents}")
            providers = list(((cfg.get("models") or {}).get("providers") or {}).keys())
            print(f"providers: {providers}")
        except json.JSONDecodeError as e:
            print(f"JSON FEHLER: {e}")
            print("Erste 300 Zeichen:", out[:300])
    else:
        print("Datei nicht lesbar oder Container nicht erreichbar")

    # Backup wiederherstellen falls nötig
    print("\n=== Backup-Dateien ===")
    out, _ = _run(ssh, "ls -la /docker/openclaw-ntw5/data/openclaw.json* 2>/dev/null")
    print(out or "(keine)")

    ssh.close()

if __name__ == "__main__":
    main()
