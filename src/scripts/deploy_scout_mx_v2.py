# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""Scout SSH helper: read config, test write, deploy camera entry."""
import paramiko
import os
import sys
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PASSWORD = os.getenv("HA_SSH_PASSWORD")
CONFIG_PATH = "/homeassistant/configuration.yaml"

CAMERA_BLOCK = """
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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(IP, port=22, username="dreadnought", password=PASSWORD, timeout=10)
    print("Verbunden mit Scout.")

    # 1. Config lesen
    code, config, err = run(ssh, f"cat {CONFIG_PATH}")
    if code != 0:
        print(f"FEHLER: Config nicht lesbar: {err}")
        ssh.close()
        return 1
    print(f"Config gelesen ({len(config)} Bytes).")

    # 2. Schon drin?
    if "name: Scout MX" in config or "camera.scout_mx" in config:
        print("Scout MX ist bereits in configuration.yaml!")
        ssh.close()
        return 0

    # 3. Backup
    code, _, err = run(ssh, f"cp {CONFIG_PATH} /tmp/configuration_backup.yaml")
    print(f"Backup: {'OK' if code == 0 else err}")

    # 4. Kamera-Block direkt an config anhaengen via tee
    escaped_block = CAMERA_BLOCK.replace("'", "'\\''")
    append_cmd = f"printf '{escaped_block}' | tee -a {CONFIG_PATH}"
    code, out, err = run(ssh, append_cmd)
    if code == 0:
        print("Kamera-Block angehaengt!")
    else:
        print(f"tee -a fehlgeschlagen: {err}")
        # Fallback: echo >> via sh
        lines = CAMERA_BLOCK.strip().split("\n")
        for line in lines:
            safe = line.replace('"', '\\"')
            run(ssh, f'echo "{safe}" >> {CONFIG_PATH}')
        code2, verify, _ = run(ssh, f"tail -8 {CONFIG_PATH}")
        if "Scout MX" in verify:
            print("Kamera-Block per echo angehaengt!")
        else:
            print("ALLE Schreibversuche fehlgeschlagen.")
            print("HINWEIS: Bitte manuell in HA File Editor den Kamera-Block einfuegen:")
            print(CAMERA_BLOCK)
            ssh.close()
            return 1

    # 5. Verify
    code, tail, _ = run(ssh, f"tail -10 {CONFIG_PATH}")
    print(f"Config-Ende:\n{tail}")

    # 6. HA core restart
    print("Starte HA Core neu...")
    code, out, err = run(ssh, "ha core restart")
    if code == 0:
        print(f"HA Neustart ausgeloest. {out}")
    else:
        print(f"HA Neustart: {out} {err}")

    ssh.close()
    print("Fertig. Warte 30 Sek auf HA-Start, dann run_scout_mx.py ausfuehren.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
