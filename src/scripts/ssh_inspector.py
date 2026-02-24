import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
# The user's env has HA_SSH_PASSWORD which might be the root or pi password
PASSWORD = os.getenv("HA_SSH_PASSWORD")
USER = os.getenv("SCOUT_USER", "pi")

def test_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Try finding the config directory
        print(f"Connecting to {USER}@{IP}:{PORT}...")
        
        # In Home Assistant Addon SSH, user is often `root` or there is no user standard,
        # but the .env specifies `pi` and `HA_SSH_PASSWORD`. Let's try `pi` first, then `root`.
        try:
            ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=10)
        except paramiko.AuthenticationException:
            print("Auth failed for 'pi'. Trying 'root'...")
            ssh.connect(IP, port=PORT, username='root', password=PASSWORD, timeout=10)
            
        print("Connected successfully!")
        
        # Find Home Assistant directory
        stdin, stdout, stderr = ssh.exec_command("find / -name configuration.yaml -path '*/config/*' -type f 2>/dev/null | head -n 1")
        config_path = stdout.read().decode().strip()
        
        if not config_path:
            stdin, stdout, stderr = ssh.exec_command("ls -la /config/configuration.yaml 2>/dev/null")
            res = stdout.read().decode().strip()
            if "configuration.yaml" in res:
                config_path = "/config/configuration.yaml"
        
        print(f"Found configuration path: {config_path}")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    test_ssh()
