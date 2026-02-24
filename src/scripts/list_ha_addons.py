import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = 22222 # Standard HA SSH port if 22 fails, but let's check
USER = "root" # HA SSH add-on usually uses root
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def list_addons():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Versuche Verbindung zu {IP}:{PORT}...")
        ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command("ha addons list")
        output = stdout.read().decode('utf-8')
        print(output)
        
        ssh.close()
    except Exception as e:
        print(f"Fehler: {e}")
        # Try port 22 if 22222 fails
        if PORT == 22222:
            try:
                print(f"Versuche Verbindung zu {IP}:22...")
                ssh.connect(IP, port=22, username=USER, password=PASSWORD, timeout=10)
                stdin, stdout, stderr = ssh.exec_command("ha addons list")
                output = stdout.read().decode('utf-8')
                print(output)
                ssh.close()
            except Exception as e2:
                print(f"Zweiter Fehler: {e2}")

if __name__ == "__main__":
    list_addons()
