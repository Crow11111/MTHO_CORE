# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import paramiko
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

HOST = os.getenv("VPS_HOST", "187.77.68.250")
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD")
KEY_PATH = os.getenv("VPS_SSH_KEY")

def connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {USER}@{HOST}...")
    try:
        if KEY_PATH and os.path.exists(KEY_PATH):
            ssh.connect(HOST, username=USER, key_filename=KEY_PATH, timeout=10)
        else:
            ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)
        return ssh
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

def read_file(ssh, path):
    print(f"Reading {path}...")
    stdin, stdout, stderr = ssh.exec_command(f"cat {path}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        return stdout.read().decode('utf-8')
    else:
        print(f"Error reading {path}: {stderr.read().decode('utf-8')}")
        return None

def main():
    ssh = connect()
    
    # 1. Check Nginx Config
    nginx_conf = read_file(ssh, "/etc/nginx/sites-available/openclaw-https.conf")
    if nginx_conf:
        print("\n--- NGINX CONFIG ---")
        print(nginx_conf)
        print("--------------------\n")
    
    # 2. Check OpenClaw Config
    # Try multiple locations
    oc_paths = [
        "/opt/core-core/openclaw-admin/data/openclaw.json",
        "/var/lib/openclaw/openclaw.json",
        "/home/node/.openclaw/openclaw.json" # Container default sometimes
    ]
    
    oc_conf = None
    for path in oc_paths:
        content = read_file(ssh, path)
        if content:
            oc_conf = content
            print(f"\n--- OPENCLAW CONFIG ({path}) ---")
            print(oc_conf)
            print("--------------------\n")
            break
            
    if not oc_conf:
        # Try finding it via docker if file not found directly
        print("Trying to find openclaw.json via docker...")
        stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}' | grep -iE 'openclaw|hvps' | head -1")
        container = stdout.read().decode('utf-8').strip()
        if container:
            print(f"Found container: {container}")
            stdin, stdout, stderr = ssh.exec_command(f"docker exec {container} cat /home/node/.openclaw/openclaw.json")
            if stdout.channel.recv_exit_status() == 0:
                print(f"\n--- OPENCLAW CONFIG (from container {container}) ---")
                print(stdout.read().decode('utf-8'))
                print("--------------------\n")

    ssh.close()

if __name__ == "__main__":
    main()
