"""OpenClaw-Container auf VPS prüfen (Status + Logs)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    os.getenv("VPS_HOST"),
    port=22,
    username=os.getenv("VPS_USER"),
    password=os.getenv("VPS_PASSWORD"),
    timeout=10,
)
_, out, _ = ssh.exec_command(
    "docker ps -a --filter name=openclaw-gateway --format '{{.Names}} {{.Status}}'; "
    "echo '---LOGS---'; docker logs openclaw-gateway 2>&1 | tail -30"
)
print(out.read().decode("utf-8", errors="replace").encode("ascii", errors="replace").decode("ascii"))
ssh.close()
