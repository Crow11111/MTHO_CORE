#!/usr/bin/env python3
"""Upload a font file to Scout (Home Assistant) via SSH."""

import paramiko
import base64
import os

# Credentials
HOST = "192.168.178.54"
PORT = 22
USERNAME = "dreadnought"
PASSWORD = "USsxrqqgF5eFqgaSUvU0in0RFTDsAK72LEIkn6gROJBTDRERgifAwuVw9qaPOahc"

# Paths
LOCAL_PATH = r"c:\Users\MtH\Documents\reain save\Skins\Sonder\@Resources\Fonts\goodtime.ttf"
REMOTE_DIR = "/config/www"
REMOTE_PATH = f"{REMOTE_DIR}/goodtime.ttf"


def main():
    # Read file and encode
    with open(LOCAL_PATH, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")

    # Connect
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST}...")
    ssh.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD)
    print("Connected.")

    # Create directory
    print(f"Creating {REMOTE_DIR}...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_DIR}")
    stdout.read()
    
    # Write file via base64 decode (chunked to avoid arg limit)
    print(f"Uploading to {REMOTE_PATH}...")
    chunk_size = 50000
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Clear file first (with sudo)
    ssh.exec_command(f"sudo sh -c '> {REMOTE_PATH}'")
    
    for i, chunk in enumerate(chunks):
        cmd = f'echo -n "{chunk}" | base64 -d | sudo tee -a {REMOTE_PATH} > /dev/null'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read().decode()
        if err:
            print(f"Chunk {i} error: {err}")
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {REMOTE_PATH}")
    print(stdout.read().decode())
    
    ssh.close()
    print("DONE")


if __name__ == "__main__":
    main()
