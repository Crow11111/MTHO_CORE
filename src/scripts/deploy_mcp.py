# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
deploy_mcp.py - MCP Server Deployment auf dem VPS (core_net)
"""
import base64, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

# dotenv laden
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

ADMIN_HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST","")).strip()
ADMIN_PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT","22"))
ADMIN_USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER","root")).strip()
ADMIN_PASS = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD","")).strip()
ADMIN_KEY  = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY","")).strip()

def connect_ssh():
    print(f"\n[SSH] {ADMIN_USER}@{ADMIN_HOST}:{ADMIN_PORT} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if ADMIN_KEY and os.path.isfile(ADMIN_KEY):
        ssh.connect(ADMIN_HOST, port=ADMIN_PORT, username=ADMIN_USER, key_filename=ADMIN_KEY, timeout=15)
    else:
        ssh.connect(ADMIN_HOST, port=ADMIN_PORT, username=ADMIN_USER, password=ADMIN_PASS or None, timeout=15)
    return ssh

def run(ssh, cmd):
    print(f"  $ {cmd[:80]}")
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)
    out = chan.recv(65535).decode("utf-8", errors="replace")
    err = chan.recv_stderr(65535).decode("utf-8", errors="replace")
    code = chan.recv_exit_status()
    if code != 0:
        print(f"    exit={code} stderr: {err.strip()[:200]}")
    return code, out, err

def b64write(ssh, path, local_file):
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    full_path = os.path.join(base_dir, local_file)
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    enc = base64.standard_b64encode(content.encode("utf-8")).decode("ascii")
    run(ssh, f"echo '{enc}' | base64 -d > {path}")

def main():
    if not ADMIN_HOST:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST oder VPS_HOST fehlt in .env.")
        return 1
    
    ssh = connect_ssh()
    run(ssh, "mkdir -p /opt/core-core/mcp-server /opt/core-core/workspace")
    
    # Files transferieren
    b64write(ssh, "/opt/core-core/mcp-server/Dockerfile", "docker/mcp-server/Dockerfile")
    b64write(ssh, "/opt/core-core/mcp-server/docker-compose.yml", "docker/mcp-server/docker-compose.yml")
    
    # Deploy
    run(ssh, "cd /opt/core-core/mcp-server && docker compose up -d --build")
    run(ssh, "docker ps | grep mcp-server")
    ssh.close()
    
    print("\n[OK] MCP Server deployed auf Port 8001 (core_net).")

if __name__ == "__main__":
    sys.exit(main())
