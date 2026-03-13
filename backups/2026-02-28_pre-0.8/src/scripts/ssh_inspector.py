"""SSH Inspector: Prüft SSH-Verbindung zum HA Pi (Advanced SSH Addon)."""
import paramiko
import os
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
USER = os.getenv("HA_SSH_USER", "dreadnought")
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def test_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {USER}@{IP}:{PORT} (Advanced SSH)...")
        ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print("Connected successfully!")
        
        _, stdout, _ = ssh.exec_command("cat /etc/hostname 2>/dev/null")
        hostname = stdout.read().decode().strip()
        print(f"Addon: {hostname}")
        
        _, stdout, _ = ssh.exec_command("ls -la /config/configuration.yaml 2>/dev/null")
        config = stdout.read().decode().strip()
        print(f"HA Config: {config if config else '/config/configuration.yaml not found'}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    test_ssh()
