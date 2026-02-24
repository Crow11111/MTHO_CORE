import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
KEY_PATH = r"C:\Users\MtH\.ollama\id_ed25519"

def try_ssh_key(user, port, key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Trying {user}@{IP}:{port} with key {key_path}...")
        key = paramiko.Ed25519Key.from_private_key_file(key_path)
        ssh.connect(IP, port=port, username=user, pkey=key, timeout=10)
        print("Connected!")
        stdin, stdout, stderr = ssh.exec_command("ha addons list")
        print(stdout.read().decode('utf-8'))
        ssh.close()
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

if __name__ == "__main__":
    for user in ["pi", "root"]:
        if try_ssh_key(user, 22, KEY_PATH):
            break
