"""Nuke WhatsApp Session: Löscht Session-Daten und startet den Container neu.
HINWEIS: Benötigt Protection Mode OFF für Docker-Zugriff."""
import paramiko
import os
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
USER = os.getenv("HA_SSH_USER", "dreadnought")
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def run_ssh_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err and "PROTECTION" not in err.upper(): print(f"Error: {err}")
    return out

def nuke_whatsapp():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Verbinde als {USER}@{IP}:{PORT}...")
        ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print(f"Verbunden als {USER}.")
    except Exception as e:
        print(f"SSH Login fehlgeschlagen: {e}")
        return

    # Finde den Container Namen (benötigt Protection Mode OFF)
    container_id = run_ssh_command(ssh, "docker ps | grep whatsapp | awk '{print $1}'")
    if not container_id:
        print("WhatsApp Container nicht gefunden.")
        print("Mögliche Ursachen:")
        print("  1. Protection Mode ist AN (Docker nicht erreichbar)")
        print("  2. WhatsApp Add-on läuft nicht")
        run_ssh_command(ssh, "find /config -name '*whatsapp*' -type d 2>/dev/null")
    else:
        print(f"Gefunden WhatsApp Container: {container_id}")
        run_ssh_command(ssh, f"docker stop {container_id}")
        
        print("Lösche Session-Dateien...")
        run_ssh_command(ssh, "find /mnt/data/supervisor/addons/data/*whatsapp* -name '*session*' -exec rm -rf {} +")
        run_ssh_command(ssh, "find /root/config/whatsapp -name '*session*' -exec rm -rf {} +")
        
        run_ssh_command(ssh, f"docker start {container_id}")
        print("Container neu gestartet.")
        
    ssh.close()

if __name__ == "__main__":
    nuke_whatsapp()
