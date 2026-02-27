"""
Setzt auf dem VPS die OpenClaw-Gateway-Config (responses.enabled: true) und startet
OpenClaw-Container neu. Kein Browser nötig – alles per SSH.

.env: VPS_HOST, VPS_USER, VPS_PASSWORD, optional OPENCLAW_GATEWAY_TOKEN

Aufruf:
  python -m src.scripts.enable_oc_responses_vps
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
TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN", "") or "").strip().strip('"')


def main() -> int:
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

    # Verzeichnis anlegen, Config schreiben oder mergen (Hostinger-Container können /var/lib/openclaw mounten)
    run = lambda cmd: _run(ssh, cmd)
    run("mkdir -p /var/lib/openclaw /var/lib/openclaw/workspace")
    # Bestehende openclaw.json einlesen und mergen, falls vorhanden
    code, out, _ = _run(ssh, "cat /var/lib/openclaw/openclaw.json 2>/dev/null || echo '{}'")
    try:
        existing = json.loads(out) if out.strip() else {}
    except json.JSONDecodeError:
        existing = {}
    # Deep-merge: unsere gateway.http.endpoints.responses haben Vorrang
    if "gateway" not in existing:
        existing["gateway"] = {}
    if "http" not in existing["gateway"]:
        existing["gateway"]["http"] = {}
    if "endpoints" not in existing["gateway"]["http"]:
        existing["gateway"]["http"]["endpoints"] = {}
    existing["gateway"]["http"]["endpoints"]["responses"] = {"enabled": True}
    if TOKEN:
        existing["gateway"]["auth"] = {"mode": "token", "token": TOKEN}
        existing["gateway"]["remote"] = {"token": TOKEN}
    merged_json = json.dumps(existing, indent=2)
    b64 = base64.standard_b64encode(merged_json.encode("utf-8")).decode("ascii")
    run(f"echo '{b64}' | base64 -d > /var/lib/openclaw/openclaw.json && chmod 644 /var/lib/openclaw/openclaw.json")
    run("chown -R 1000:1000 /var/lib/openclaw 2>/dev/null || true")
    print("Config gesetzt: gateway.http.endpoints.responses.enabled = true")

    # Alle Container finden, die nach OpenClaw aussehen (Name oder Image)
    code, out, _ = _run(ssh, "docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null || true")
    to_restart = []
    for line in (out or "").strip().splitlines():
        if not line:
            continue
        parts = line.split(None, 1)
        name = (parts[0] or "").lower()
        image = (parts[1] if len(parts) > 1 else "").lower()
        if "openclaw" in name or "openclaw" in image or "hvps-openclaw" in image:
            to_restart.append(parts[0])

    if to_restart:
        for c in to_restart:
            print(f"Starte Container neu: {c}")
            _run(ssh, f"docker restart {c}")
    else:
        # Fallback: bekannter Name
        code, _, _ = _run(ssh, "docker restart openclaw-gateway 2>/dev/null")
        if code == 0:
            print("Container openclaw-gateway neugestartet.")
        else:
            print("Hinweis: Kein OpenClaw-Container gefunden (docker ps -a). Wenn OpenClaw nur im Hostinger-Panel läuft, Config dort prüfen oder Container-Namen auf dem VPS mit 'docker ps' ansehen.")

    ssh.close()
    print("Fertig. In 10–20 s erneut senden: python -m src.scripts.send_offene_punkte_to_oc")
    return 0


def _run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return code, out, err


if __name__ == "__main__":
    sys.exit(main())
