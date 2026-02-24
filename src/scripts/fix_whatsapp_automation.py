import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(out)
    if err: print(f"ERR: {err}")
    return out

def fix():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP, port=PORT, username="dreadnought", password=PASSWORD, timeout=10)
    print("Verbunden!")
    
    # Use sed to replace event type in-place (no SFTP needed)
    result = run(ssh, "sed -i 's/whatsapp_message_received/new_whatsapp_message/g' /root/config/automations.yaml && echo 'PATCHED'")
    
    if "PATCHED" in (result or ""):
        print("Event-Type erfolgreich gepatcht!")
    
    # Verify
    run(ssh, "grep -n 'whatsapp' /root/config/automations.yaml")
    
    ssh.close()
    print("\nJetzt HA in der Oberfläche neu starten (oder Automatisierungen neu laden).")

if __name__ == "__main__":
    fix()
