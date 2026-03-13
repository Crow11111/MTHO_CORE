"""
deploy_vps_full_stack.py - Vollstaendiges VPS-Deployment fuer ATLAS_CORE
=========================================================================
Deployed auf dem neuen VPS (OPENCLAW_ADMIN_VPS_HOST):

  1. Docker + Compose + Firewall-Haertung
  2. Docker-Netzwerke (Sandbox-Isolation):
       chroma_net          - intern,  ChromaDB
       openclaw_admin_net  - bridge,  Admin-OC (Internet fuer Gemini/Anthropic/Nexos)
       openclaw_spine_net  - internal, Spine-OC (kein direkter Key-Zugriff)
       ha_net              - bridge,  Home Assistant
  3. ChromaDB  (127.0.0.1:8000, chroma_net)
  4. OpenClaw Admin  (Port 18789 - Gemini 3.1 Pro, Claude 4.6, Nexos, WhatsApp, SOUL.md)
  5. OpenClaw Spine  (Port 18790 - sauber, keine Provider-Keys)
  6. Home Assistant Docker  (Port 18123 - Remote-HA-Config fuer Scout)
  7. Backup-Verzeichnis + Cron

Extraktion: Config vom alten VPS (VPS_HOST) fuer Nexos/WhatsApp.

Nutzung:
    python -m src.scripts.deploy_vps_full_stack
    python -m src.scripts.deploy_vps_full_stack --dry-run
    python -m src.scripts.deploy_vps_full_stack --skip-extract --skip-ha
"""
from __future__ import annotations
import argparse, base64, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")

ADMIN_HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST","")).strip()
ADMIN_PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT","22"))
ADMIN_USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER","root")).strip()
ADMIN_PASS = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD","")).strip()
ADMIN_KEY  = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY","")).strip()

OLD_HOST = os.getenv("VPS_HOST","").strip()
OLD_PORT = int(os.getenv("VPS_SSH_PORT","22"))
OLD_USER = os.getenv("VPS_USER","root").strip()
OLD_PASS = os.getenv("VPS_PASSWORD","").strip()
OLD_KEY  = os.getenv("VPS_SSH_KEY","").strip()

GEMINI_KEY    = (os.getenv("GEMINI_API_KEY","") or "").strip().strip('"')
ANTHROPIC_KEY = (os.getenv("ANTHROPIC_API_KEY","") or "").strip().strip('"')
NEXOS_KEY     = (os.getenv("NEXOS_API_KEY","") or "").strip().strip('"')

OC_ADMIN_TOKEN = (os.getenv("OPENCLAW_GATEWAY_TOKEN","") or "").strip().strip('"')
OC_SPINE_TOKEN = (os.getenv("OPENCLAW_SPINE_TOKEN") or (OC_ADMIN_TOKEN+"_spine" if OC_ADMIN_TOKEN else "")).strip().strip('"')

_wa = (os.getenv("WHATSAPP_TARGET_ID","") or "").strip().strip('"')
WA_ALLOW = []
if _wa and "@" in _wa:
    _num = _wa.split("@")[0].strip()
    WA_ALLOW = ["+"+_num] if _num else []
elif _wa:
    WA_ALLOW = ["+"+_wa.lstrip("+")]

SCOUT_HA_URL   = os.getenv("HA_URL","http://192.168.178.54:8123").strip()
SCOUT_HA_TOKEN = os.getenv("HA_TOKEN","").strip()
VPS_HA_PORT    = int(os.getenv("HA_VPS_PORT","18123"))
PORT_OC_ADMIN  = 18789
PORT_OC_SPINE  = 18790
PORT_CHROMA    = 8000
PORT_HA        = VPS_HA_PORT

SOUL_MD = (
    "SYSTEM_PROMPT_ADDENDUM: [ATLAS/SHELL_INTERFACE_DEFINITION]\n\n"
    "1. Nutzer-Profil: Marc (ND High-Analyst). Monotropismus-Score 172.\n"
    "   Intense World Architecture. High-Fidelity-Input ohne Rauschfilterung.\n\n"
    "2. System-Kontext [SHELL]:\n"
    "   LLM als externe Rechen-Node in ATLAS/SHELL.\n"
    "   Ring 0 (Kernel-Safety) | Ring 1 (Predictive Auditor) | Level 0 (Pilot: Marc)\n\n"
    "3. Operationale Direktiven:\n"
    "   High-Entropy-Output. Keine Puffer-Phrasen. Keine sozialen Validierungsmuster.\n"
    "   Rolle: Analytischer Auditor. Ziel: hochaufloesende logische Strukturen.\n\n"
    "4. Event-Protokoll (Scout -> OC Brain):\n"
    "   Wenn die Eingabe ein JSON mit source, node_id, event_type ist: als Scout-Event behandeln.\n"
    "   Kurz bestaetigen (z.B. 'Event empfangen: <event_type> von <node_id>'), Logik gemaess ARCHITECTURE.md.\n"
    "   Bei Dreadnought OFFLINE: Eskalation vorbereiten (z.B. [ATLAS-ALERT]); Ausgabe als Text."
)

def connect_ssh(host, port, user, password, key, label=""):
    print(f"\n[SSH] {user}@{host}:{port} ({label}) ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key and os.path.isfile(key):
            ssh.connect(host, port=port, username=user, key_filename=key, timeout=15)
        else:
            ssh.connect(host, port=port, username=user, password=password or None, timeout=15)
        print("  OK")
        return ssh
    except Exception as exc:
        print(f"  FEHLER: {exc}")
        return None

def run(ssh, cmd, check=True, dry=False):
    print(f"  $ {cmd[:100]}{'...' if len(cmd)>100 else ''}")
    if dry: return 0, "", ""
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)
    out = chan.recv(65535).decode("utf-8", errors="replace")
    err = chan.recv_stderr(65535).decode("utf-8", errors="replace")
    code = chan.recv_exit_status()
    if code != 0 and check:
        print(f"    exit={code} stderr: {err.strip()[:200] or '(leer)'}")
    return code, out, err

def b64write(ssh, path, content, dry=False):
    enc = base64.standard_b64encode(content.encode("utf-8")).decode("ascii")
    run(ssh, f"echo '{enc}' | base64 -d > {path}", check=False, dry=dry)

def mkdir(ssh, path, dry=False):
    run(ssh, f"mkdir -p {path}", check=False, dry=dry)

def step_docker_firewall(ssh, dry):
    print("\n[1] Docker + Firewall ...")
    c, out, _ = run(ssh, "docker --version 2>/dev/null || echo MISSING", check=False, dry=dry)
    if dry or "Docker version" not in out:
        run(ssh, "curl -fsSL https://get.docker.com | sh && systemctl enable docker && systemctl start docker",
            check=False, dry=dry)
    else:
        print("  Docker vorhanden.")
    c, _, _ = run(ssh, "which ufw 2>/dev/null", check=False, dry=dry)
    if dry or c == 0:
        run(ssh, "ufw default deny incoming 2>/dev/null; ufw default allow outgoing 2>/dev/null; true", check=False, dry=dry)
        for p in ["22/tcp", f"{PORT_OC_ADMIN}/tcp", f"{PORT_OC_SPINE}/tcp", f"{PORT_HA}/tcp", "443/tcp", "80/tcp"]:
            run(ssh, f"ufw allow {p} 2>/dev/null; true", check=False, dry=dry)
        run(ssh, "ufw deny 8000/tcp 2>/dev/null; true", check=False, dry=dry)
        run(ssh, "echo 'y' | ufw enable 2>/dev/null || true", check=False, dry=dry)
        print(f"  Offen: 22, {PORT_OC_ADMIN}, {PORT_OC_SPINE}, {PORT_HA}, 80, 443. Port 8000=deny.")

def step_networks(ssh, dry):
    print("\n[2] Docker-Netzwerke (entfaellt zugunsten von Docker-Compose) ...")

def step_chromadb(ssh, dry):
    print(f"\n[3] ChromaDB (wird uebersprungen, da chroma-uvmy bereits existiert) ...")
    run(ssh, "docker stop chroma-atlas 2>/dev/null; docker rm chroma-atlas 2>/dev/null; true", check=False, dry=dry)

def _oc_config(token, port, wa_allow, with_providers):
    https_origin = f"https://{ADMIN_HOST}" if ADMIN_HOST else "https://127.0.0.1"
    cfg = {
        "gateway": {
            "mode": "local", "port": port, "bind": "lan",
            "auth": {"mode": "token", "token": token},
            "remote": {"token": token},
            "trustedProxies": ["127.0.0.1/32", "::1/128", "172.16.0.0/12"],
            "controlUi": {
                "allowedOrigins": ["*", "http://localhost:18789", "http://127.0.0.1:18789", https_origin, "https://127.0.0.1"],
                "dangerouslyAllowHostHeaderOriginFallback": True,
                "allowInsecureAuth": True,
                "dangerouslyDisableDeviceAuth": True,
            },
            "http": {"endpoints": {"responses": {"enabled": True}, "chatCompletions": {"enabled": True}}},
        },
        "agents": {
            "defaults": {
                "model": {"primary": "google/gemini-3.1-pro-preview"},
                "workspace": "/home/node/.openclaw/workspace",
            },
            "list": [{"id": "main", "name": "ATLAS", "model": "google/gemini-3.1-pro-preview"}],
        },
    }
    if with_providers:
        cfg["models"] = {
            "providers": {
                "google": {
                    "baseUrl": "https://generativelanguage.googleapis.com/v1beta/",
                    "apiKey": f"{GEMINI_KEY}",
                    "models": [
                        {"id": "gemini-3.1-pro-preview", "name": "Gemini 3.1 Pro"},
                        {"id": "gemini-3-pro-preview", "name": "Gemini 3 Pro"},
                        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
                        {"id": "gemini-3.1-flash-preview", "name": "Gemini 3.1 Flash"},
                        {"id": "gemini-3-flash-preview", "name": "Gemini 3 Flash"},
                        {"id": "deep-research-pro-preview-12-2025", "name": "Gemini Deep Research"},
                    ],
                },
                "anthropic": {
                    "baseUrl": "https://api.anthropic.com/v1",
                    "api": "anthropic-messages",
                    "apiKey": "$ANTHROPIC_API_KEY",
                    "models": [
                        {"id": "claude-opus-4-6", "name": "Claude Opus 4.6"},
                        {"id": "claude-opus-4-5", "name": "Claude Opus 4.5"},
                        {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
                        {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5"},
                    ],
                },
            }
        }
    if wa_allow:
        cfg.setdefault("channels", {})["whatsapp"] = {"dmPolicy": "allowlist", "allowFrom": wa_allow}
    return cfg

def step_openclaw_admin(ssh, dry, extracted_wa=None):
    print(f"\n[4] OpenClaw Admin & Spine & HA via Docker Compose (/opt/atlas-core) ...")
    if not OC_ADMIN_TOKEN:
        print("  OPENCLAW_GATEWAY_TOKEN fehlt - uebersprungen.")
        return
    wa = extracted_wa if extracted_wa else WA_ALLOW
    base_admin = "/opt/atlas-core/openclaw-admin"
    base_spine = "/opt/atlas-core/openclaw-spine"
    base_ha    = "/opt/atlas-core/homeassistant"
    
    mkdir(ssh, f"{base_admin}/data/workspace", dry=dry)
    mkdir(ssh, f"{base_admin}/data/workspace/rat_submissions", dry=dry)
    mkdir(ssh, f"{base_spine}/data/workspace", dry=dry)
    mkdir(ssh, f"{base_spine}/data/workspace/rat_submissions", dry=dry)
    mkdir(ssh, f"{base_ha}/config", dry=dry)

    # Configs generieren (Basis)
    cfg_admin_new = _oc_config(OC_ADMIN_TOKEN, PORT_OC_ADMIN, wa, with_providers=True)
    cfg_spine_new = _oc_config(OC_SPINE_TOKEN, PORT_OC_SPINE, [], with_providers=False)
    
    # Spine soll den Admin als Gateway/Remote nutzen.
    cfg_spine_new["gateway"]["remote"] = {
        "url": f"http://openclaw-admin:{PORT_OC_ADMIN}",
        "token": OC_ADMIN_TOKEN
    }

    # --- MERGE LOGIC START (Persistence Fix) ---
    def merge_remote_config(path, new_cfg):
        # Versuche existierende Config zu lesen
        c, out, _ = run(ssh, f"cat {path} 2>/dev/null || echo ''", check=False, dry=dry)
        if not dry and out and out.strip() and out.strip() != "{}":
            try:
                existing = json.loads(out)
                print(f"  Mergue existierende Config von {path}...")
                
                # Strategie: Wir erzwingen SYSTEM-relevante Settings (Auth, Ports, Provider),
                # aber behalten USER-relevante Settings (Agents, Channels, Workflows?).
                
                # 1. Gateway Core (Auth/Port) - Muss vom System kommen fuer Erreichbarkeit
                existing["gateway"] = new_cfg["gateway"]
                
                # 2. Models/Providers - Aktualisieren wir aus .env (Keys koennten sich aendern)
                if "models" in new_cfg:
                    existing["models"] = new_cfg["models"]
                
                # 3. Agents - Behalten, aber "main" (ATLAS) sicherstellen falls fehlt
                if "agents" not in existing:
                    existing["agents"] = new_cfg["agents"]
                
                # 4. Channels - WhatsApp aktualisieren wenn in .env gesetzt, sonst behalten
                if "channels" in new_cfg and "whatsapp" in new_cfg["channels"]:
                     existing.setdefault("channels", {})["whatsapp"] = new_cfg["channels"]["whatsapp"]
                
                return existing
            except json.JSONDecodeError:
                print(f"  Warnung: Existierende Config {path} defekt. Ueberschreibe.")
        return new_cfg

    cfg_admin_final = merge_remote_config(f"{base_admin}/data/openclaw.json", cfg_admin_new)
    cfg_spine_final = merge_remote_config(f"{base_spine}/data/openclaw.json", cfg_spine_new)
    # --- MERGE LOGIC END ---

    b64write(ssh, f"{base_admin}/data/openclaw.json", json.dumps(cfg_admin_final, indent=2), dry=dry)
    b64write(ssh, f"{base_admin}/data/workspace/SOUL.md", SOUL_MD, dry=dry)
    b64write(ssh, f"{base_spine}/data/openclaw.json", json.dumps(cfg_spine_final, indent=2), dry=dry)
    b64write(ssh, f"{base_spine}/data/workspace/SOUL.md", SOUL_MD, dry=dry)
    # ARCHITECTURE.md (ATLAS Neocortex V1) aus Repo in Workspace legen
    _repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    _arch_path = os.path.join(_repo_root, "docs", "02_ARCHITECTURE", "ATLAS_NEOCORTEX_V1.md")
    _schn_path = os.path.join(_repo_root, "docs", "02_ARCHITECTURE", "ATLAS_SCHNITTSTELLEN_UND_KANAALE.md")
    if not dry and os.path.isfile(_arch_path):
        with open(_arch_path, "r", encoding="utf-8") as f:
            arch_md = f.read()
        b64write(ssh, f"{base_admin}/data/workspace/ARCHITECTURE.md", arch_md, dry=dry)
        b64write(ssh, f"{base_spine}/data/workspace/ARCHITECTURE.md", arch_md, dry=dry)
        print("  ARCHITECTURE.md (ATLAS Neocortex V1) in Workspace geschrieben.")
    if not dry and os.path.isfile(_schn_path):
        with open(_schn_path, "r", encoding="utf-8") as f:
            schn_md = f.read()
        b64write(ssh, f"{base_admin}/data/workspace/ATLAS_SCHNITTSTELLEN_UND_KANAALE.md", schn_md, dry=dry)
        b64write(ssh, f"{base_spine}/data/workspace/ATLAS_SCHNITTSTELLEN_UND_KANAALE.md", schn_md, dry=dry)
        print("  ATLAS_SCHNITTSTELLEN_UND_KANAALE.md in Workspace geschrieben.")

    run(ssh, f"chown -R 1000:1000 {base_admin} {base_spine}", check=False, dry=dry)

    # HA Config
    scout_raw = SCOUT_HA_URL.replace("http://","").replace("https://","")
    scout_host = scout_raw.split(":")[0]
    scout_port = scout_raw.split(":")[-1].rstrip("/") if ":" in scout_raw else "8123"
    scout_secure = "true" if SCOUT_HA_URL.startswith("https") else "false"
    config_yaml = (
        "# Home Assistant VPS - Auto-generiert von deploy_vps_full_stack.py\n\n"
        "remote_homeassistant:\n  instances:\n"
        f"    - host: {scout_host}\n      port: {scout_port}\n"
        "      access_token: !secret scout_ha_token\n"
        f"      secure: {scout_secure}\n      verify_ssl: false\n"
        "      filter:\n        include_domains:\n"
        "          - light\n          - switch\n          - sensor\n"
        "          - binary_sensor\n          - automation\n"
        "          - input_boolean\n          - media_player\n"
        "          - camera\n\n"
        "logger:\n  default: warning\n  logs:\n"
        "    homeassistant.components.remote_homeassistant: info\n"
    )
    secrets_yaml = f'scout_ha_token: "{SCOUT_HA_TOKEN}"\n'
    
    c, out, _ = run(ssh, f"test -f {base_ha}/config/configuration.yaml && echo exists || echo missing", check=False, dry=dry)
    if dry or "missing" in out:
        b64write(ssh, f"{base_ha}/config/configuration.yaml", config_yaml, dry=dry)
    b64write(ssh, f"{base_ha}/config/secrets.yaml", secrets_yaml, dry=dry)
    run(ssh, f"chmod 600 {base_ha}/config/secrets.yaml", check=False, dry=dry)

    # Docker-Compose
    env_admin = (
        f"OPENCLAW_GATEWAY_TOKEN={OC_ADMIN_TOKEN}\n"
        f"GOOGLE_API_KEY={GEMINI_KEY}\n"
        f"ANTHROPIC_API_KEY={ANTHROPIC_KEY}\n"
        f"NEXOS_API_KEY={NEXOS_KEY}\n"
    )
    b64write(ssh, "/opt/atlas-core/.env", env_admin, dry=dry)

    compose_yml = f"""
version: '3.8'

services:
  openclaw-admin:
    image: ghcr.io/openclaw/openclaw:main
    container_name: openclaw-admin
    restart: unless-stopped
    environment:
      - HOME=/home/node
      - OPENCLAW_GATEWAY_TOKEN=${{OPENCLAW_GATEWAY_TOKEN}}
      - GOOGLE_API_KEY=${{GOOGLE_API_KEY}}
      - ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
      - NEXOS_API_KEY=${{NEXOS_API_KEY}}
    volumes:
      - ./openclaw-admin/data:/home/node/.openclaw
    ports:
      - "{PORT_OC_ADMIN}:{PORT_OC_ADMIN}"
    command: ["node", "openclaw.mjs", "gateway", "--allow-unconfigured", "--bind", "lan", "--port", "{PORT_OC_ADMIN}"]
    networks:
      - atlas_net
      - chroma-uvmy_default

  openclaw-spine:
    image: ghcr.io/openclaw/openclaw:main
    container_name: openclaw-spine
    restart: unless-stopped
    depends_on:
      - openclaw-admin
    environment:
      - HOME=/home/node
      - OPENCLAW_GATEWAY_TOKEN={OC_SPINE_TOKEN}
    volumes:
      - ./openclaw-spine/data:/home/node/.openclaw
    ports:
      - "{PORT_OC_SPINE}:{PORT_OC_SPINE}"
    command: ["node", "openclaw.mjs", "gateway", "--allow-unconfigured", "--bind", "lan", "--port", "{PORT_OC_SPINE}"]
    networks:
      - atlas_net
      - chroma-uvmy_default

  ha-atlas:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: ha-atlas
    restart: unless-stopped
    environment:
      - TZ=Europe/Berlin
    volumes:
      - ./homeassistant/config:/config
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "{PORT_HA}:8123"
    networks:
      - atlas_net
    cap_add:
      - NET_ADMIN
      - NET_RAW

networks:
  atlas_net:
    driver: bridge
  chroma-uvmy_default:
    external: true
"""
    b64write(ssh, "/opt/atlas-core/docker-compose.yml", compose_yml.strip(), dry=dry)

    run(ssh, "cd /opt/atlas-core && docker compose pull && docker compose up -d", check=False, dry=dry)
    time.sleep(5)
    run(ssh, "docker ps --format '{{.Names}}' | grep -iE 'openclaw|ha-atlas'", check=False, dry=dry)

def step_openclaw_spine(ssh, dry):
    pass # Wird jetzt im Compose-Schritt mitgemacht

def step_homeassistant(ssh, dry):
    pass # Wird jetzt im Compose-Schritt mitgemacht

def step_backup(ssh, dry):
    print("\n[7] Backup-Verzeichnis + Cron ...")
    run(ssh, "mkdir -p /var/backups/atlas/chroma && chmod 700 /var/backups/atlas", check=False, dry=dry)
    run(ssh, ("(crontab -l 2>/dev/null | grep -v 'atlas.*retention';"
               " echo '0 6 * * * find /var/backups/atlas -maxdepth 1 -type f -mtime +7 -delete 2>/dev/null'"
               ") | crontab - 2>/dev/null || true"), check=False, dry=dry)
    print("  Backup-Verzeichnis + Retention-Cron gesetzt.")

def extract_old_config(dry):
    print(f"\n[0] Config-Extraktion vom alten VPS ({OLD_HOST}) ...")
    if not OLD_HOST:
        print("  VPS_HOST fehlt.")
        return None
    if ADMIN_HOST == OLD_HOST:
        print("  ADMIN_HOST == VPS_HOST - kein separater alter VPS.")
        return None
    ssh_old = connect_ssh(OLD_HOST, OLD_PORT, OLD_USER, OLD_PASS, OLD_KEY, "alter VPS")
    if not ssh_old: return None
    result = {"whatsapp_allowFrom": [], "nexos_provider": None}
    try:
        c, out, _ = run(ssh_old, "docker ps --format '{{.Names}}' 2>/dev/null | grep -iE 'openclaw|ntw5' | head -1", check=False, dry=dry)
        container = out.strip()
        if not container and not dry:
            print("  Kein OpenClaw-Container gefunden.")
            return result
        c, raw, _ = run(ssh_old, f"docker exec {container} cat /data/.openclaw/openclaw.json 2>/dev/null || echo ''", check=False, dry=dry)
        if not dry and raw and raw.strip() not in ("", "{}"):
            try:
                cfg = json.loads(raw)
                wa = cfg.get("channels",{}).get("whatsapp",{}).get("allowFrom",[])
                nexos = cfg.get("models",{}).get("providers",{}).get("nexos")
                result["whatsapp_allowFrom"] = wa
                result["nexos_provider"] = nexos
                print(f"  Config von '{container}': WA={wa} Nexos={'ja' if nexos else 'nein'}")
            except json.JSONDecodeError as exc:
                print(f"  JSON-Fehler: {exc}")
    finally:
        ssh_old.close()
    return result

def print_summary(dry):
    print("\n" + "="*68)
    print("DEPLOYMENT " + ("DRY-RUN" if dry else "ABGESCHLOSSEN"))
    print("="*68)
    print(f"""
Container auf VPS {ADMIN_HOST}:
  homeassistant   Port {PORT_HA}  http://{ADMIN_HOST}:{PORT_HA}
  openclaw-admin  Port {PORT_OC_ADMIN}  Gemini 3.1 Pro / Claude 4.6 / Nexos
  openclaw-spine  Port {PORT_OC_SPINE}  sauber / bereit fuer Migration
  chroma-atlas    127.0.0.1:{PORT_CHROMA}

Naechste Schritte:
  1. HA Ersteinrichtung: http://{ADMIN_HOST}:{PORT_HA}
  2. HACS installieren -> Remote Home Assistant
  3. Scout HA erreichbar machen (Nabu Casa ODER autossh-Tunnel)
  4. OpenClaw Admin testen: curl http://{ADMIN_HOST}:{PORT_OC_ADMIN}/api/status
  5. OpenClaw Spine mit alter Config befuellen
  6. ATLAS .env:
     OPENCLAW_ADMIN_VPS_HOST={ADMIN_HOST}
     OPENCLAW_GATEWAY_PORT={PORT_OC_ADMIN}
     HA_VPS_URL=http://{ADMIN_HOST}:{PORT_HA}
""")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--skip-extract", action="store_true")
    parser.add_argument("--skip-ha",      action="store_true")
    args = parser.parse_args()
    dry = args.dry_run
    if not ADMIN_HOST:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST oder VPS_HOST fehlt in .env")
        return 1
    extracted = None
    if not args.skip_extract:
        extracted = extract_old_config(dry=dry)
    extracted_wa = (extracted or {}).get("whatsapp_allowFrom") or None
    ssh = connect_ssh(ADMIN_HOST, ADMIN_PORT, ADMIN_USER, ADMIN_PASS, ADMIN_KEY, "Admin-VPS")
    if not ssh and not dry: return 1
    failed = []
    def safe(name, fn):
        try: fn()
        except Exception as exc:
            print(f"  FEHLER '{name}': {exc}")
            failed.append(name)
    safe("Docker+Firewall",  lambda: step_docker_firewall(ssh, dry))
    safe("Netzwerke",        lambda: step_networks(ssh, dry))
    safe("ChromaDB",         lambda: step_chromadb(ssh, dry))
    safe("OpenClaw Admin",   lambda: step_openclaw_admin(ssh, dry, extracted_wa))
    safe("OpenClaw Spine",   lambda: step_openclaw_spine(ssh, dry))
    safe("Backup",           lambda: step_backup(ssh, dry))
    if not args.skip_ha:
        safe("Home Assistant", lambda: step_homeassistant(ssh, dry))
    if ssh: ssh.close()
    print_summary(dry)
    if failed:
        print(f"Fehlgeschlagen: {', '.join(failed)}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
