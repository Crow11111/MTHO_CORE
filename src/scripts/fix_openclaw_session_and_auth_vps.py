# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Behebt auf dem OpenClaw-VPS per SSH:
1. Session-Lock: Container stoppen, Lock-Dateien und defekte Session im Volume löschen.
2. Google-Auth: auth-profiles.json für main und agent mit GEMINI_API_KEY aus .env schreiben.
3. Agent-Verzeichnis für den zweiten Agenten (agent) anlegen.
4. Container wieder starten.

Damit der Lock wirklich weg ist, wird der Container gestoppt und ein temporärer Alpine-Container
mit --volumes-from genutzt, um im Volume zu löschen/schreiben.

.env: VPS_HOST, VPS_USER, VPS_PASSWORD, GEMINI_API_KEY

Aufruf:
  python -m src.scripts.fix_openclaw_session_and_auth_vps
"""
from __future__ import annotations

import base64
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("VPS_HOST", "").strip()
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY", "") or "").strip().strip('"')


def _run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err


def main():
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1
    print(f"Verbinde mit {USER}@{HOST} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if KEY_PATH and os.path.isfile(KEY_PATH):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
    except Exception as e:
        print(f"SSH-Fehler: {e}")
        return 1

    code, out, _ = _run(ssh, "docker ps -a --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|hvps' | head -1")
    container = (out or "").strip() or "openclaw-gateway"
    print(f"Container: {container}")

    print("Stoppe Container ...")
    _run(ssh, f"docker stop {container}")
    print("  Container gestoppt.")

    d = "/data/.openclaw"
    rm_part = f"rm -f {d}/agents/main/sessions/*.lock {d}/agents/main/sessions/47ebc8c5-6854-430e-83d9-6c2e30efbc3d.jsonl 2>/dev/null"
    mk_part = f"mkdir -p {d}/agents/main/agent {d}/agents/agent/agent"
    sh_cmd = rm_part + "; " + mk_part + "; echo done"
    code, out, err = _run(ssh, f"docker run --rm --volumes-from {container} alpine sh -c '{sh_cmd}'")
    if code != 0:
        print("Warnung:", err or out)
    else:
        print("  Session-Locks und defekte Session gelöscht, Agent-Verzeichnisse angelegt.")

    if GEMINI_API_KEY:
        auth_body = json.dumps({"google": {"apiKey": GEMINI_API_KEY}})
        auth_b64 = base64.standard_b64encode(auth_body.encode("utf-8")).decode("ascii")
        for aid in ("main", "agent"):
            _run(ssh, f"docker run --rm --volumes-from {container} alpine sh -c \"echo '{auth_b64}' | base64 -d > {d}/agents/{aid}/agent/auth-profiles.json\"")
        print("  auth-profiles.json für main und agent gesetzt.")
    else:
        print("  GEMINI_API_KEY fehlt in .env.")

    print(f"Starte {container} ...")
    code, out, err = _run(ssh, f"docker start {container}")
    ssh.close()
    if code != 0:
        print("Fehler Start:", err or out)
        return 1
    print("Fertig. In ~15 s Chat erneut testen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
