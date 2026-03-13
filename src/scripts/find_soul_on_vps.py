# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""Such auf dem Hostinger-VPS nach vorhandener SOUL.md (alte OpenClaw-Installation)."""
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
    port=int(os.getenv("VPS_SSH_PORT", "22")),
    username=os.getenv("VPS_USER"),
    password=os.getenv("VPS_PASSWORD"),
    timeout=15,
)

# Suche nach SOUL.md; dann Inhalt von Nutzer-Pfaden und (falls gefunden) erste Treffer aus Docker
cmd = (
    "echo '=== Suche ==='; find /root /var/lib/openclaw /home -name 'SOUL.md' 2>/dev/null | head -20; "
    "echo '--- Inhalt /var/lib/openclaw/workspace/SOUL.md ---'; "
    "cat /var/lib/openclaw/workspace/SOUL.md 2>/dev/null || echo '(nicht vorhanden)'; "
    "echo '--- Inhalt /root/.openclaw/workspace/SOUL.md ---'; "
    "cat /root/.openclaw/workspace/SOUL.md 2>/dev/null || echo '(nicht vorhanden)'"
)
_, out, err = ssh.exec_command(cmd)
text = out.read().decode("utf-8", errors="replace")
err = err.read().decode("utf-8", errors="replace")
ssh.close()

# Safe print für Windows-Konsole
out_safe = (text + (err if err else "")).encode("ascii", errors="replace").decode("ascii")
print(out_safe)
