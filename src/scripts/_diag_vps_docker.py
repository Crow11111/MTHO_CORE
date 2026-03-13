# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""VPS-Diagnose: Docker/ChromaDB-Status per SSH."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))
import paramiko

host = os.getenv("VPS_HOST", "").strip()
user = os.getenv("VPS_USER", "root")
pw = os.getenv("VPS_PASSWORD", "")
key = os.getenv("VPS_SSH_KEY", "").strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    if key and os.path.isfile(key):
        ssh.connect(host, port=22, username=user, key_filename=key, timeout=15)
    else:
        ssh.connect(host, port=22, username=user, password=pw or None, timeout=15)
    print("SSH OK zu", host)
    cmds = [
        'docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"',
        'ss -tlnp | grep 8000 || echo "Port 8000: nichts lauscht"',
        'docker ps --filter name=chroma --format "{{.Names}} {{.Status}}" || echo "kein chroma container"',
    ]
    for cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        print(f"\n--- {cmd} ---")
        if out: print(out)
        if err: print(err)
    ssh.close()
except Exception as e:
    print(f"SSH FEHLER: {e}")
