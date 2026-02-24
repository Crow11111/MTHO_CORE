import paramiko
import os
import sys
from dotenv import load_dotenv

# Fix encoding on Windows terminals
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
PASSWORD = os.getenv("HA_SSH_PASSWORD")

AUTOMATION_YAML = """
- alias: "ATLAS: Weiterleitung WhatsApp eingehend"
  trigger:
    - platform: event
      event_type: whatsapp_message_received
  action:
    - service: rest_command.atlas_whatsapp_webhook
      data:
        payload: "{{ trigger.event.data }}"
"""

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

def wire_up():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP, port=PORT, username="dreadnought", password=PASSWORD, timeout=10)
    print("Verbunden!")

    # Check automations.yaml for ATLAS entry
    auto_content, _ = run(ssh, "cat /root/config/automations.yaml")
    
    if "ATLAS: Weiterleitung WhatsApp" in auto_content:
        print("ATLAS Automatisierung bereits vorhanden!")
    else:
        print("Füge Automatisierung hinzu...")
        sftp = ssh.open_sftp()
        with sftp.open("/root/config/automations.yaml", "a") as f:
            f.write(AUTOMATION_YAML)
        sftp.close()
        print("Automatisierung hinzugefügt!")
    
    # Reload HA config
    print("Lade HA neu...")
    out, err = run(ssh, "ha core reload 2>&1 || ha core restart 2>&1")
    print(out or err or "OK!")
    
    print("\nFertig! Sende jetzt eine Test-WhatsApp und beobachte den ATLAS-Log.")
    ssh.close()

if __name__ == "__main__":
    wire_up()
