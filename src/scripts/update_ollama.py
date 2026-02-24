import paramiko
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PASSWORD = os.getenv("HA_SSH_PASSWORD")

def try_ssh_command(user, port, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Trying {user}@{IP}:{port}...")
        ssh.connect(IP, port=port, username=user, password=PASSWORD, timeout=10)
        print(f"Connected as {user}!")
        stdin, stdout, stderr = ssh.exec_command(command)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        ssh.close()
        return out, err
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    users = ["pi", "root", "ha"]
    ports = [22, 22222]
    
    found = False
    for port in ports:
        for user in users:
            out, err = try_ssh_command(user, port, "ha addons list")
            if out is not None:
                print("--- Add-ons ---")
                print(out)
                found = True
                # Look for Ollama
                addons = out.split("\n")
                ollama_slug = None
                for line in addons:
                    if "ollama" in line.lower():
                        # The output of 'ha addons list' is usually a table or list
                        # Let's just try updating both possible slugs if we find them
                        print(f"Potential Ollama addon found in line: {line}")
                
                # If we are here, we are connected and can try the update
                print("Attempting to update ollama...")
                # We need the slug. Usually 'local_ollama' or '5c432238_ollama'
                # Let's try to find it specifically
                stdin, stdout, stderr = ssh_connect_and_exec(user, port, "ha addons list --raw") # if raw exists
                # For now, let's just try common slugs if seen
                break
        if found: break
    
    if not found:
        print("Could not connect to Scout with provided credentials.")
