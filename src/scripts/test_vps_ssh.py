# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""Test SSH-Verbindung zum Hostinger-VPS (OpenClaw / ChromaDB)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

HOST = os.getenv("VPS_HOST", "")
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")


def test_vps_ssh():
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER nicht in .env gesetzt.")
        return False
    if not PASSWORD:
        print("HINWEIS: VPS_PASSWORD fehlt – ggf. SSH-Key verwenden.")
    print(f"SSH-Test: {USER}@{HOST}:{PORT} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=10)
        print("OK: Verbunden mit VPS.")
        _, stdout, _ = ssh.exec_command("hostname && whoami && id")
        out = stdout.read().decode().strip()
        print(out)
        # ChromaDB / OpenClaw prüfen
        _, so, _ = ssh.exec_command("ls -la /root 2>/dev/null | head -5")
        print("root dir:", so.read().decode().strip() or "(nicht lesbar)")
        ssh.close()
        return True
    except Exception as e:
        print(f"FEHLER: {e}")
        if ssh:
            try:
                ssh.close()
            except Exception:
                pass
        return False


if __name__ == "__main__":
    ok = test_vps_ssh()
    sys.exit(0 if ok else 1)
