"""Check SSH addons on HA via SSH as dreadnought."""
import paramiko, os
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    "192.168.178.54", port=22,
    username=os.getenv("HA_SSH_USER", "dreadnought"),
    password=os.getenv("HA_SSH_PASSWORD"),
    timeout=10
)
print("Connected as", os.getenv("HA_SSH_USER"))

cmds = [
    "whoami",
    "cat /etc/hostname",
    "docker ps --format '{{.Names}}' 2>/dev/null",
    "ls /addons/ 2>/dev/null || echo 'no /addons/'",
    "supervisord --version 2>/dev/null || echo 'no supervisord'",
    "ha addons list 2>/dev/null || echo 'ha CLI not available for this user'",
]

for cmd in cmds:
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"\n$ {cmd}")
    if out:
        print(f"  {out}")
    if err:
        print(f"  [err] {err}")

ssh.close()
