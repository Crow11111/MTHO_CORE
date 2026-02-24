import paramiko
import os
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
PASSWORD = os.getenv("HA_SSH_PASSWORD")
USER = os.getenv("HA_USER", "HA_AC") # Let's try the HA_USER or root or pi

def run_ssh_command(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print(f"Error: {err}")
    return out

def nuke_whatsapp():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    users_to_try = [
        ("dreadnought", PASSWORD),
        ("root", PASSWORD),
        ("HA_AC", os.getenv("HA_AC_PASSWORD")),
        ("pi", PASSWORD)
    ]
    
    connected = False
    for u, p in users_to_try:
        try:
            print(f"Versuche Login als {u}...")
            ssh.connect(IP, port=PORT, username=u, password=p, timeout=5)
            print(f"Erfolgreich eingeloggt als {u}!")
            connected = True
            break
        except Exception as e:
            print(f"Fehlgeschlagen für {u}.")
            
    if not connected:
        print("Kein SSH Login möglich.")
        return

    # Finde den Container Namen
    container_id = run_ssh_command(ssh, "docker ps | grep whatsapp | awk '{print $1}'")
    if not container_id:
        print("WhatsApp Add-on Container nicht gefunden. Läuft das Addon?")
        
        # Vielleicht ist der Docker Daemon nicht direkt erreichbar (Schutz im Add-on).
        print("Versuche direkten Dateizugriff im config Verzeichnis...")
        run_ssh_command(ssh, "find / -name '*whatsapp*' -type d 2>/dev/null")
    else:
        print(f"Gefunden WhatsApp Container: {container_id}")
        run_ssh_command(ssh, f"docker stop {container_id}")
        
        # Lösche Add-on Daten unter /data oder /config
        # We find the volume bindings
        inspect = run_ssh_command(ssh, f"docker inspect {container_id} | grep -A 10 Mounts")
        print("Mounts:")
        print(inspect)
        
        # Alternativ können wir den data Ordner des supervisor leeren
        print("Lösche mögliche Session-Dateien...")
        run_ssh_command(ssh, "find /mnt/data/supervisor/addons/data/*whatsapp* -name '*session*' -exec rm -rf {} +")
        run_ssh_command(ssh, "find /root/config/whatsapp -name '*session*' -exec rm -rf {} +")
        
        run_ssh_command(ssh, f"docker start {container_id}")
        print("Container neu gestartet.")
        
    ssh.close()

if __name__ == "__main__":
    nuke_whatsapp()
