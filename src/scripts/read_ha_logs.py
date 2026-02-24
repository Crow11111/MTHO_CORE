import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.178.54", port=22, username="dreadnought", password=os.getenv("HA_SSH_PASSWORD"), timeout=10)

print("Verbunden! Lese HA Logs...")

# Read last 100 lines of HA log
stdin, stdout, _ = ssh.exec_command("tail -100 /root/config/home-assistant.log 2>/dev/null")
logs = stdout.read().decode('utf-8', errors='replace')

# Filter for relevant lines
keywords = ["atlas", "whatsapp", "rest_command", "new_whatsapp", "automation", "8000", "error"]
matching = []
for line in logs.split('\n'):
    for kw in keywords:
        if kw.lower() in line.lower():
            matching.append(line)
            break

print("\n=== RELEVANTE LOG-EINTRÄGE ===")
print('\n'.join(matching[-50:]) if matching else "Keine relevanten Treffer.")

ssh.close()
