import os
import time
from dotenv import load_dotenv
from fabric import Connection
from invoke.exceptions import UnexpectedExit

# Load environment variables
load_dotenv()

# Configuration
# SCOUT_IP should be in .env or passed as arg. For now, we look for it or prompt.
SCOUT_HOST = os.getenv("SCOUT_HOST", "pi@192.168.178.XX") # Placeholder
SCOUT_KEY_PATH = os.getenv("SCOUT_KEY_PATH", "c:/CORE/.ssh/id_rsa_scout") # Placeholder

def deploy_scout():
    print(f"Deploying Scout to {SCOUT_HOST}...")
    
    # Initialize connection
    # Note: We assume key-based auth. If password, we need connect_kwargs.
    try:
        c = Connection(host=SCOUT_HOST, connect_kwargs={"key_filename": SCOUT_KEY_PATH})
        c.run("echo 'Connection successful'", hide=True)
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Please verify SCOUT_HOST and SCOUT_KEY_PATH in .env")
        return

    # 1. Create directory structure
    remote_dir = "/home/pi/atlas_scout"
    c.run(f"mkdir -p {remote_dir}/src/edge")
    c.run(f"mkdir -p {remote_dir}/src/services")
    c.run(f"mkdir -p {remote_dir}/docker")

    # 2. Upload files (using SCP/SFTP)
    # We use put() from fabric/paramiko
    print("Uploading files...")
    # Tar the source files locally to preserve structure, then upload and untar?
    # Or just upload individually if few.
    # Let's use individual put for simplicity of this script, or better:
    # Use rsync if available, but Windows->Linux rsync is tricky.
    # Simple recursion or tarball is best.
    
    # Create local tarball
    os.system("tar -czf scout_payload.tar.gz src/edge src/services docker/scout .env")
    
    # Upload tarball
    c.put("scout_payload.tar.gz", f"{remote_dir}/scout_payload.tar.gz")
    
    # Extract
    with c.cd(remote_dir):
        c.run("tar -xzf scout_payload.tar.gz")
        c.run("rm scout_payload.tar.gz")
        
    # 3. Build and Run Docker
    print("Building and starting Scout container...")
    with c.cd(f"{remote_dir}/docker/scout"):
        # We need to make sure we point to the context root correctly for the build
        # The docker-compose should use 'context: ../../'
        # Let's check docker-compose.yml
        pass

    # We might need to adjust docker-compose.yml to point to relative paths correctly on the remote
    # or just run docker build manually.
    # Let's assume docker-compose works if paths are correct.
    
    with c.cd(remote_dir):
        # We run compose from the root of the deployed folder, pointing to the file
        try:
            c.run("docker compose -f docker/scout/docker-compose.yml up -d --build")
            print("Scout deployment successful!")
        except UnexpectedExit as e:
            print(f"Docker Compose failed: {e}")

    # Clean up local tar
    if os.path.exists("scout_payload.tar.gz"):
        os.remove("scout_payload.tar.gz")

if __name__ == "__main__":
    deploy_scout()
