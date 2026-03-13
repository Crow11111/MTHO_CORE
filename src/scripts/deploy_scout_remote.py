# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import time
from dotenv import load_dotenv
from fabric import Connection
from invoke.exceptions import UnexpectedExit

# Load environment variables
load_dotenv()

# Configuration
SCOUT_IP = os.getenv("SCOUT_IP", "192.168.178.54")
SCOUT_USER = os.getenv("HA_SSH_USER", "dreadnought")
SCOUT_HOST = f"{SCOUT_USER}@{SCOUT_IP}"
SCOUT_PASSWORD = os.getenv("HA_SSH_PASSWORD")

def deploy_scout():
    print(f"Deploying Scout to {SCOUT_HOST}...")

    # Initialize connection
    try:
        if SCOUT_PASSWORD:
            c = Connection(host=SCOUT_HOST, connect_kwargs={"password": SCOUT_PASSWORD})
        else:
            c = Connection(host=SCOUT_HOST, connect_kwargs={"key_filename": SCOUT_KEY_PATH})
        c.run("echo 'Connection successful'", hide=True)
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Please verify SCOUT_HOST and SCOUT_KEY_PATH in .env")
        return

    # 1. Create directory structure
    remote_dir = "/home/dreadnought/core_scout"
    c.run(f"mkdir -p {remote_dir}/src/edge")
    c.run(f"mkdir -p {remote_dir}/src/services")
    c.run(f"mkdir -p {remote_dir}/docker")

    # 2. Upload files (using SCP/SFTP)
    print("Uploading files...")
    
    # Create local tarball
    os.system("tar -czf scout_payload.tar.gz src/edge src/services src/logic_core src/config src/daemons docker/scout .env")

    # 2. Upload files via python directly over SSH to avoid SCP hangs on HA OS
    print("Uploading files via remote file write...")
    try:
        import base64
        with open("scout_payload.tar.gz", "rb") as f:
            encoded_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Split into 50kb chunks to not crash the shell buffer
        chunk_size = 50000
        chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
        
        c.run(f"rm -f {remote_dir}/payload.b64")
        for i, chunk in enumerate(chunks):
            print(f"Uploading chunk {i+1}/{len(chunks)}...")
            c.run(f"echo '{chunk}' >> {remote_dir}/payload.b64")
            
        c.run(f"base64 -d {remote_dir}/payload.b64 > {remote_dir}/scout_payload.tar.gz")
        c.run(f"rm {remote_dir}/payload.b64")
        print("Upload successful.")
    except Exception as e:
        print(f"Chunked Base64 upload failed: {e}")

    # Extract
    with c.cd(remote_dir):
        c.run("tar -xzf scout_payload.tar.gz")
        c.run("rm scout_payload.tar.gz")
        
    # 2b. Setup OS-Level Crystal Daemon (Systemd)
    print("\n--- HINWEIS ZUR AUSFÜHRUNG AUF HOME ASSISTANT OS ---")
    print("Die Dateien wurden erfolgreich auf das Home Assistant System kopiert.")
    print("Da Home Assistant OS jedoch ein hochgradig restriktives Alpine Linux ohne systemd und tc ist,")
    print("kann der OS-Daemon hier nicht als klassischer Linux-Service installiert werden.")
    print("Das Fraktale Padding läuft stattdessen sicher über die Python-Backend-Ebene (llm_interface / chroma).")

    # Clean up local tar
    if os.path.exists("scout_payload.tar.gz"):
        os.remove("scout_payload.tar.gz")

if __name__ == "__main__":
    deploy_scout()
