# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Fügt die USB-Kamera (MX am Scout) in die Home Assistant configuration.yaml ein.
Nutzt platform: ffmpeg mit input: /dev/video0.
Setzt name: Scout MX -> entity_id: camera.scout_mx.

Voraussetzung:
- SSH-Zugang zum Scout (in .env: SCOUT_IP, HA_SSH_PASSWORD)
- Kamera ist am Raspi 5 eingesteckt (/dev/video0)
"""
import paramiko
import os
import sys
import time
from dotenv import load_dotenv

# Fix encoding on Windows terminals
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv("c:/CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
PASSWORD = os.getenv("HA_SSH_PASSWORD")

# YAML-Block für die Kamera (Achtung: Einrückung wichtig!)
CAMERA_YAML = """
ffmpeg:

camera:
  - platform: ffmpeg
    input: /dev/video0
    name: Scout MX
"""

def run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return exit_status, out, err

def main():
    if not PASSWORD:
        print("FEHLER: HA_SSH_PASSWORD in .env fehlt.")
        return 1

    print(f"Verbinde mit Scout ({IP})...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(IP, port=PORT, username="dreadnought", password=PASSWORD, timeout=10)
    except Exception as e:
        print(f"SSH-Verbindungsfehler: {e}")
        return 1
    print("Verbunden!")

    # 1. Prüfen ob /dev/video0 existiert
    code, out, err = run(ssh, "ls -l /dev/video0")
    if code != 0:
        print("WARNUNG: /dev/video0 auf Scout nicht gefunden. Ist die Kamera eingesteckt?")
        # Wir machen trotzdem weiter, da der Pfad korrekt sein sollte
    else:
        print("Kamera-Device /dev/video0 gefunden.")

    # 2. configuration.yaml prüfen
    config_path = "/root/config/configuration.yaml"
    code, content, err = run(ssh, f"cat {config_path}")
    if code != 0:
        print(f"FEHLER: Konnte {config_path} nicht lesen: {err}")
        ssh.close()
        return 1

    if "name: Scout MX" in content or "camera.scout_mx" in content:
        print("Kamera 'Scout MX' scheint schon in configuration.yaml zu sein.")
    else:
        print("Füge Kamera-Konfiguration hinzu...")
        # Anhängen mit printf um Newlines sicherzustellen
        cmd = f"printf \"{CAMERA_YAML}\" >> {config_path}"
        code, out, err = run(ssh, cmd)
        if code != 0:
            print(f"Fehler beim Schreiben: {err}")
            ssh.close()
            return 1
        print("Konfiguration geschrieben.")

    # 3. HA neu laden
    print("Starte HA Core neu (kann kurz dauern)...")
    # ha core restart ist zuverlässiger als reload für neue Plattformen (ffmpeg)
    code, out, err = run(ssh, "ha core restart")
    if code == 0:
        print("Neustart ausgelöst.")
    else:
        print(f"Fehler beim Neustart: {out} {err}")
    
    ssh.close()
    
    print("\nWarte 20 Sekunden auf HA-Start...")
    time.sleep(20)
    print("Fertig. Bitte jetzt 'python src/scripts/run_scout_mx.py' ausführen um zu prüfen und .env zu setzen.")

if __name__ == "__main__":
    sys.exit(main())
