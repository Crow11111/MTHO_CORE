import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def run_ssh_command(user, port, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {user}@{IP}:{port}...")
        ssh.connect(IP, port=port, username=user, password=PASSWORD, timeout=15)
        print("Connected! Executing command...")
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        ssh.close()
        return out, err
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    # The user specifically requested SSH.
    # We will try root first as it's common for HA SSH terminal.
    out, err = run_ssh_command("root", 22, "ha addons list")
    if out:
        print("Addons found:")
        print(out)
        # Identify Ollama slug
        # Output is usually of the form:
        # slug: name version (state)
        lines = out.split('\n')
        ollama_slug = None
        for line in lines:
            if "ollama" in line.lower():
                parts = line.split()
                if parts:
                    ollama_slug = parts[0]
                    break
        
        if ollama_slug:
            print(f"Found Ollama slug: {ollama_slug}. Updating...")
            up_out, up_err = run_ssh_command("root", 22, f"ha addons update {ollama_slug}")
            print("Update output:")
            print(up_out)
            if up_err: print(f"Update error: {up_err}")
        else:
            print("Ollama addon not found in list.")
    else:
        print(f"Failed to connect or execute: {err}")
