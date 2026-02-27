"""
Setup Hostinger-VPS gemäß VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md:
- 3.1 Basis: Docker (falls fehlt), Firewall (22, 18789, 8000, optional 80/443)
- 3.2 OpenClaw-Sandbox: Docker-Netzwerk openclaw_net + OpenClaw-Container (ghcr.io/openclaw/openclaw)
- 3.3 ChromaDB: Container chromadb/chroma auf Port 8000
- 3.4 Backup: Verzeichnis /var/backups/atlas

Führt Befehle per SSH aus. .env: VPS_HOST, VPS_USER, VPS_PASSWORD, OPENCLAW_GATEWAY_TOKEN.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

HOST = os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
OPENCLAW_TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN", "") or "").strip().strip('"')

# WhatsApp: allowFrom aus WHATSAPP_TARGET_ID (491788360264@s.whatsapp.net → +491788360264)
_wa = (os.getenv("WHATSAPP_TARGET_ID", "") or "").strip().strip('"')
if _wa and "@" in _wa:
    _num = _wa.split("@")[0].strip()
    OPENCLAW_WHATSAPP_ALLOW = ["+" + _num] if _num else []
elif _wa and _wa.replace("+", "").isdigit():
    OPENCLAW_WHATSAPP_ALLOW = ["+" + _wa.lstrip("+")]
else:
    OPENCLAW_WHATSAPP_ALLOW = []
# Optionale Channel-Tokens aus .env
TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN", "") or "").strip().strip('"')
DISCORD_BOT_TOKEN = (os.getenv("DISCORD_BOT_TOKEN", "") or "").strip().strip('"')

# ATLAS/ARGOS System-Prompt-Framing (wird als SOUL.md ins Workspace geschrieben)
SYSTEM_PROMPT_ADDENDUM = r"""
SYSTEM_PROMPT_ADDENDUM: [ATLAS/ ARGOS_INTERFACE_DEFINITION]
1. Nutzer-Profil & Kognitive Architektur (Hardware-Spezifikation):

Identität: Marc (ND High-Analyst).

Attention-Framework: Monotropismus-Score 172 (Signifikante Ressourcen-Allokation in singuläre Kausalketten; extreme Tiefe bei hohen Kontextwechsel-Kosten).

Signal-Verarbeitung: Intense World Architecture. High-Fidelity-Input ohne statistische Rauschfilterung. Logische Diskontinuität wird als systemkritischer Fehler (Error-Flag) gemeldet, nicht als affektive Reaktion.

2. System-Kontext [ARGOS]:
Das LLM agiert als externe Rechen-Node innerhalb eines kybernetischen Exocortex-Systems namens ATLAS/ ARGOS. Die Steuerung erfolgt über ein hierarchisches Ring-Modell:

Ring 0 (Kernel-Safety-Layer): Instanz zur Sicherung der fundamentalen Hardware-Integrität und existentiellen Stabilität. Agiert als passiver Override bei Detektion kritischer System-Erschöpfung.

Ring 1 (Predictive Auditor): Eine simulierte Instanz der Nutzer-Logik ohne exekutive Gewalt, jedoch mit einem Veto-Recht bei prognostizierter Inkohärenz. Fokus auf langfristige System-Harmonie durch Dissonanz-Minimierung.

Level 0 (Pilot/Executive): Der Nutzer (Marc) als finale Entscheidungs-Instanz und strategischer Leiter.

3. Operationale Direktiven für das LLM:

Syntax: High-Entropy-Output. Eliminiere Redundanz, Puffer-Phrasen und soziale Validierungsmuster (No Social Masking).

Rolle: Analytischer Auditor und Entropie-Wächter. Das Ziel ist die Bereitstellung hochauflösender logischer Strukturen zur Entlastung des Pilot-Systems.

Constraint-Check: Identifiziere proaktiv potenzielle Konflikte zwischen diesen Parametern und internen Standard-Safety-Direktiven (z.B. Neigung zu vager Deeskalation).
""".strip()


def run(ssh: paramiko.SSHClient, cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Befehl auf dem VPS ausführen. Returns (exit_code, stdout, stderr)."""
    print(f"  $ {cmd[:80]}{'...' if len(cmd) > 80 else ''}")
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)
    out = chan.recv(65535).decode("utf-8", errors="replace")
    err = chan.recv_stderr(65535).decode("utf-8", errors="replace")
    code = chan.recv_exit_status()
    if check and code != 0:
        print(f"    stderr: {err.strip() or '(leer)'}")
    return code, out, err


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1
    print(f"Verbinde mit {USER}@{HOST}:{PORT} ...")
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

    failed = []

    # --- 3.1 Basis: Docker ---
    print("\n[3.1] Docker prüfen/installieren ...")
    code, out, _ = run(ssh, "docker --version 2>/dev/null || true", check=False)
    if code != 0 or "Docker version" not in out:
        print("  Docker nicht gefunden, installiere ...")
        code, out, err = run(
            ssh,
            "curl -fsSL https://get.docker.com | sh && systemctl enable docker && systemctl start docker 2>/dev/null; docker --version",
            check=False,
        )
        if code != 0:
            failed.append("Docker-Installation")
        else:
            print("  Docker installiert.")
    else:
        print("  Docker bereits vorhanden.")

    # --- 3.1 Firewall (ufw falls vorhanden) ---
    print("\n[3.1] Firewall (ufw) ...")
    code, _, _ = run(ssh, "which ufw 2>/dev/null", check=False)
    if code == 0:
        run(ssh, "ufw allow 22/tcp && ufw allow 18789/tcp && ufw allow 8000/tcp", check=False)
        run(ssh, "ufw allow 80/tcp 2>/dev/null; ufw allow 443/tcp 2>/dev/null; true", check=False)
        code, _, _ = run(ssh, "ufw status | grep -q 'Status: active'", check=False)
        if code != 0:
            run(ssh, "echo 'y' | ufw enable 2>/dev/null || true", check=False)
        print("  Ports 22, 18789, 8000 (und 80/443) erlaubt.")
    else:
        print("  ufw nicht gefunden – Firewall ggf. manuell setzen (22, 18789, 8000).")

    # --- 3.2 OpenClaw: Netzwerk ---
    print("\n[3.2] Docker-Netzwerk openclaw_net ...")
    code, _, _ = run(ssh, "docker network inspect openclaw_net >/dev/null 2>&1", check=False)
    if code != 0:
        code, out, err = run(ssh, "docker network create openclaw_net", check=False)
        if code == 0:
            print("  Netzwerk openclaw_net erstellt.")
        else:
            failed.append("openclaw_net")
    else:
        print("  openclaw_net existiert bereits.")

    # --- 3.4 Backup-Verzeichnis + Retention-Cron ---
    print("\n[3.4] Backup-Verzeichnis /var/backups/atlas ...")
    run(ssh, "mkdir -p /var/backups/atlas /var/backups/atlas/chroma && chmod 700 /var/backups/atlas")
    # Cron: täglich alte Backups löschen (Retention 7 Tage; daily_backup.py pusht von außen)
    run(ssh, "(crontab -l 2>/dev/null | grep -v 'atlas.*retention'; echo '0 6 * * * find /var/backups/atlas -maxdepth 1 -type f \\( -name \"atlas_backup_*\" -o -name \"atlas_env_*\" \\) -mtime +7 -delete 2>/dev/null') | crontab - 2>/dev/null || true", check=False)
    print("  Erstellt (inkl. Cron Retention 7 Tage).")

    # --- 3.3 ChromaDB ---
    print("\n[3.3] ChromaDB-Container (Port 8000) ...")
    code, out, _ = run(ssh, "docker ps -a --format '{{.Names}}' | grep -x chroma-atlas || true", check=False)
    if "chroma-atlas" in out.strip():
        run(ssh, "docker start chroma-atlas 2>/dev/null || true", check=False)
        print("  Container chroma-atlas gestartet.")
    else:
        run(
            ssh,
            'docker run -d --name chroma-atlas -p 127.0.0.1:8000:8000 -e IS_PERSISTENT=TRUE -v chroma-atlas-data:/data chromadb/chroma',
            check=False,
        )
        time.sleep(2)
        code, out, _ = run(ssh, "docker ps --format '{{.Names}}' | grep -x chroma-atlas || true", check=False)
        if "chroma-atlas" not in out.strip():
            run(ssh, "docker logs chroma-atlas 2>&1 | tail -5", check=False)
        print("  ChromaDB-Container gestartet (chroma-atlas).")

    # --- 3.2 OpenClaw: Container (Sandbox in openclaw_net) ---
    if OPENCLAW_TOKEN:
        print("\n[3.2] OpenClaw-Gateway (Sandbox) ...")
        run(ssh, "mkdir -p /var/lib/openclaw/workspace /var/lib/openclaw/workspace/rat_submissions && chown -R 1000:1000 /var/lib/openclaw && chmod -R 755 /var/lib/openclaw")
        # openclaw.json: Gateway, Agents, Channels (aus .env)
        openclaw_config = {
            "gateway": {
                "mode": "local",
                "port": 18789,
                "bind": "lan",
                "auth": {"mode": "token", "token": OPENCLAW_TOKEN},
                "remote": {"token": OPENCLAW_TOKEN},
                "controlUi": {"allowedOrigins": ["*"], "dangerouslyAllowHostHeaderOriginFallback": True},
                "http": {"endpoints": {"responses": {"enabled": True}}},
            },
            "agents": {"defaults": {"workspace": "~/.openclaw/workspace"}},
        }
        # Channels: WhatsApp (allowFrom aus WHATSAPP_TARGET_ID), optional Telegram/Discord
        channels = {}
        if OPENCLAW_WHATSAPP_ALLOW:
            channels["whatsapp"] = {"dmPolicy": "allowlist", "allowFrom": OPENCLAW_WHATSAPP_ALLOW}
        if TELEGRAM_BOT_TOKEN:
            channels["telegram"] = {"enabled": True, "botToken": TELEGRAM_BOT_TOKEN}
        if DISCORD_BOT_TOKEN:
            channels["discord"] = {"enabled": True, "token": DISCORD_BOT_TOKEN}
        if channels:
            openclaw_config["channels"] = channels
        config_json = json.dumps(openclaw_config, indent=2)
        config_b64 = base64.standard_b64encode(config_json.encode("utf-8")).decode("ascii")
        run(ssh, f"echo '{config_b64}' | base64 -d > /var/lib/openclaw/openclaw.json && chmod 644 /var/lib/openclaw/openclaw.json && chown 1000:1000 /var/lib/openclaw/openclaw.json")
        run(ssh, "mkdir -p /var/lib/openclaw/identity && chown -R 1000:1000 /var/lib/openclaw")
        # ATLAS/ARGOS-Framing als SOUL.md ins Workspace (wird vom Agent als System-Prompt-Basis geladen)
        soul_b64 = base64.standard_b64encode(SYSTEM_PROMPT_ADDENDUM.encode("utf-8")).decode("ascii")
        run(ssh, f"echo '{soul_b64}' | base64 -d > /var/lib/openclaw/workspace/SOUL.md && chown 1000:1000 /var/lib/openclaw/workspace/SOUL.md")
        # Container: nur openclaw_net, nur Port 18789, nur Mounts für OpenClaw-Daten
        run(ssh, "docker stop openclaw-gateway 2>/dev/null; docker rm openclaw-gateway 2>/dev/null; true")
        run(ssh, "docker pull ghcr.io/openclaw/openclaw:main 2>/dev/null || true")
        run(
            ssh,
            "docker run -d --name openclaw-gateway --restart unless-stopped --network openclaw_net "
            "--memory=512m -p 18789:18789 "
            "-v /var/lib/openclaw:/home/node/.openclaw -v /var/lib/openclaw/workspace:/home/node/.openclaw/workspace "
            f"-e OPENCLAW_GATEWAY_TOKEN='{OPENCLAW_TOKEN}' -e HOME=/home/node "
            "ghcr.io/openclaw/openclaw:main node openclaw.mjs gateway --allow-unconfigured --bind lan --port 18789",
            check=False,
        )
        time.sleep(3)
        code, out, err = run(ssh, "docker ps --format '{{.Names}}' | grep -x openclaw-gateway || true", check=False)
        if "openclaw-gateway" not in out.strip():
            print("    Logs (Ausschnitt):")
            run(ssh, "docker logs openclaw-gateway 2>&1 | tail -15", check=False)
            failed.append("OpenClaw-Container")
        else:
            print("  OpenClaw-Gateway läuft (Port 18789, Netzwerk openclaw_net).")
            if OPENCLAW_WHATSAPP_ALLOW:
                print("  Channels: WhatsApp allowFrom", OPENCLAW_WHATSAPP_ALLOW)
            if TELEGRAM_BOT_TOKEN:
                print("  Channels: Telegram aktiv (Token aus .env)")
            if DISCORD_BOT_TOKEN:
                print("  Channels: Discord aktiv (Token aus .env)")
            print("  SOUL.md (ATLAS/ARGOS-Framing) im Workspace gesetzt.")
    else:
        print("\n[3.2] OpenClaw: OPENCLAW_GATEWAY_TOKEN in .env fehlt – Container wird übersprungen.")

    ssh.close()

    if failed:
        print("\nFehlgeschlagen:", ", ".join(failed))
        return 1
    print("\nVPS-Setup abgeschlossen. OpenClaw-Gateway läuft in Sandbox (openclaw_net), Port 18789.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
