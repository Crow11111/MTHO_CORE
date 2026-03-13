# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""VPS: ChromaDB Port-Mapping diagnostizieren und fixen."""
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
if key and os.path.isfile(key):
    ssh.connect(host, port=22, username=user, key_filename=key, timeout=15)
else:
    ssh.connect(host, port=22, username=user, password=pw or None, timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"\n--- {cmd} ---")
    if out: print(out)
    if err: print("ERR:", err)
    return out

print("SSH OK zu", host)

run('find / -maxdepth 4 -name "docker-compose*" 2>/dev/null | head -20')
run('docker inspect core_chroma_state --format "{{json .HostConfig.PortBindings}}" 2>/dev/null')
run('docker inspect chroma-uvmy-chromadb-1 --format "{{json .HostConfig.PortBindings}}" 2>/dev/null')
run('docker inspect core_chroma_state --format "{{json .Config.ExposedPorts}}" 2>/dev/null')

# Prüfe ob socat verfügbar ist
socat_check = run("which socat 2>/dev/null || echo 'NOT_FOUND'")

# Fix: socat als Port-Forwarder 127.0.0.1:8000 -> chroma-uvmy auf 32768
# Oder: iptables nat redirect
actual_port = run('docker port chroma-uvmy-chromadb-1 8000 2>/dev/null')
print(f"\nChroma-uvmy tatsächlicher Host-Port: {actual_port}")

if actual_port:
    mapped_port = actual_port.split(":")[-1] if ":" in actual_port else ""
    print(f"Extrahierter Port: {mapped_port}")

    if "NOT_FOUND" not in socat_check:
        # socat installiert -> verwende socat
        run("pkill -f 'socat.*TCP-LISTEN:8000' 2>/dev/null || true")
        run(f"nohup socat TCP-LISTEN:8000,bind=127.0.0.1,reuseaddr,fork TCP:127.0.0.1:{mapped_port} </dev/null >/dev/null 2>&1 &")
        import time; time.sleep(1)
        result = run("ss -tlnp | grep 8000")
        if "8000" in (result or ""):
            print("\n=== FIX ERFOLGREICH: Port 8000 jetzt auf VPS erreichbar (socat -> chroma-uvmy) ===")
        else:
            print("\n=== socat gestartet aber Port 8000 noch nicht sichtbar ===")
    else:
        print("socat nicht installiert. Installiere...")
        run("apt-get update -qq && apt-get install -y -qq socat 2>/dev/null")
        run("pkill -f 'socat.*TCP-LISTEN:8000' 2>/dev/null || true")
        run(f"nohup socat TCP-LISTEN:8000,bind=127.0.0.1,reuseaddr,fork TCP:127.0.0.1:{mapped_port} </dev/null >/dev/null 2>&1 &")
        import time; time.sleep(1)
        result = run("ss -tlnp | grep 8000")
        if "8000" in (result or ""):
            print("\n=== FIX ERFOLGREICH: Port 8000 jetzt auf VPS erreichbar ===")
        else:
            print("\n=== Fallback: socat nicht erfolgreich ===")
else:
    print("Konnte chroma-uvmy Port nicht ermitteln")

ssh.close()
