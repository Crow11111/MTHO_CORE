import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
PASSWORD = os.getenv("HA_SSH_PASSWORD")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(IP, port=PORT, username="dreadnought", password=PASSWORD, timeout=10)
print("Verbunden!")

# First validate the config
stdin, stdout, stderr = ssh.exec_command("ha core check 2>&1")
check = stdout.read().decode('utf-8', errors='replace')
print(f"Config Check:\n{check}")

# Restart HA Core
stdin, stdout, stderr = ssh.exec_command("ha core restart 2>&1")
result = stdout.read().decode('utf-8', errors='replace')
print(f"Restart: {result or 'Befehl abgeschickt!'}")

ssh.close()
