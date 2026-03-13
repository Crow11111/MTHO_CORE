# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""List HA Addons via SSH (requires Protection Mode OFF for ha CLI)."""
import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
USER = os.getenv("HA_SSH_USER", "dreadnought")
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def list_addons():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Verbinde als {USER}@{IP}:{PORT}...")
        ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=10)
        
        # ha CLI benötigt Protection Mode OFF
        _, stdout, stderr = ssh.exec_command("ha addons list 2>/dev/null")
        output = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        if output.strip():
            print(output)
        elif "PROTECTION" in err.upper() or not output.strip():
            print("ha CLI nicht verfügbar (Protection Mode ist AN).")
            print("Deaktiviere Protection Mode im HA UI unter:")
            print("  Settings → Add-ons → Advanced SSH → Protection Mode OFF")
        
        ssh.close()
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    list_addons()
