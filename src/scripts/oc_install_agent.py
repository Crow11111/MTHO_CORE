"""
Installiert einen Agent/Skill auf OC (OpenClaw) per SSH auf dem VPS.

Führt im OpenClaw-Container (oder im OC-Kontext auf dem Host) aus:
  clawhub install <agent_name>
(oder clawdhub, je nachdem was im Container verfügbar ist)

.env: VPS_HOST, VPS_USER, VPS_PASSWORD (oder VPS_SSH_KEY)

Aufruf:
  python -m src.scripts.oc_install_agent self-improving-agent
  python -m src.scripts.oc_install_agent self-improving-agent --container openclaw-gateway
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

HOST = os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()


def _safe_print(s: str) -> None:
    if not s:
        return
    try:
        print(s)
    except UnicodeEncodeError:
        # Konsolen-Encoding (z. B. cp1252) mit Ersatz für nicht darstellbare Zeichen
        import sys
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(s.encode(enc, errors="replace").decode(enc))


def run(ssh, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return code, out, err


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    agent_name = args[0] if args else "self-improving-agent"
    container_override = None
    for a in sys.argv[1:]:
        if a.startswith("--container="):
            container_override = a.split("=", 1)[1].strip()

    import paramiko
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

    try:
        if container_override:
            containers = [container_override]
        else:
            code, out, _ = run(ssh, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|gateway' || true")
            containers = [n.strip() for n in (out or "").splitlines() if n.strip()]
            if not containers:
                print("Kein OpenClaw-Container gefunden. Optional: --container=NAME angeben.")
                return 1

        container = containers[0]
        print(f"Container: {container}")
        print(f"Installiere auf OC: {agent_name}\n")

        # clawdhub oder clawhub (je nach OpenClaw-Version)
        for cmd_name in ["clawdhub", "clawhub"]:
            install_cmd = f"docker exec {container} {cmd_name} install {agent_name} 2>&1"
            code, out, err = run(ssh, install_cmd)
            full = (out or "") + (err or "")
            if code == 0:
                _safe_print(full or "OK.")
                return 0
            if "not found" in full.lower() or "command not found" in full.lower():
                continue
            print(f"({cmd_name}): Exit {code}")
            _safe_print(full or err)
            return 1

        # Fallback: npx clawhub install (wenn Node im Container)
        install_cmd = f"docker exec {container} sh -c 'npx --yes clawhub install {agent_name}' 2>&1"
        code, out, err = run(ssh, install_cmd)
        full = (out or "") + (err or "")
        if code == 0:
            _safe_print(full or "OK.")
            return 0
        print("Hinweis: clawhub/clawdhub im Container nicht gefunden. Evtl. im Hostinger-Panel oder in der OC-Doku die Installationsanleitung für Agents prüfen.")
        _safe_print(full or err)
        return 1
    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
