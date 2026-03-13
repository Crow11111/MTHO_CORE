<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# VPS-Slim Deployment

**Ziel:** Scout-Forwarded-Text bei HA-Ausfall auf VPS verarbeiten.

| Parameter | Wert |
|-----------|------|
| VPS | 187.77.68.250 |
| SSH Key | `c:\CORE\.ssh\id_ed25519_hostinger` |
| User | root |
| Port | 8001 |

## Voraussetzungen

- CORE `src/` inkl. Abhängigkeiten (atlas_llm, HAClient, logic_core.context_injector)
- `.env` mit: `HA_WEBHOOK_TOKEN`, `GEMINI_API_KEY`, `HA_URL`, `HA_TOKEN`, `CHROMA_HOST` (optional)

## Automatischer Deploy (empfohlen)

```powershell
# .env: VPS_HOST=187.77.68.250, VPS_USER=root, VPS_SSH_KEY=c:\CORE\.ssh\id_ed25519_hostinger
python -m src.scripts.deploy_vps_slim
```

Kopiert `src/` + `Dockerfile.vps`, baut Docker-Image, startet Container auf Port 8001. Benötigt `.env` auf VPS unter `VPS_DEPLOY_PATH` (default `/opt/core-core`).

## Manueller Deploy

```powershell
# 1. SSH-Verbindung testen
ssh -i c:\CORE\.ssh\id_ed25519_hostinger root@187.77.68.250 "echo OK"

# 2. Code + .env auf VPS kopieren (tar+scp wie deploy_agi_state.py)
# Oder: python -m src.scripts.deploy_vps_slim

# 3. Auf VPS: Service starten
ssh -i c:\CORE\.ssh\id_ed25519_hostinger root@187.77.68.250
cd /opt/core-core
source .venv/bin/activate  # oder: python -m venv .venv && pip install -r src/requirements.txt
VPS_SLIM_PORT=8001 python -m uvicorn src.api.vps_slim:app --host 0.0.0.0 --port 8001
```

## systemd (empfohlen)

```ini
# /etc/systemd/system/core-vps-slim.service
[Unit]
Description=CORE VPS-Slim Failover
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/core-core
EnvironmentFile=/opt/core-core/.env
ExecStart=/opt/core-core/.venv/bin/python -m uvicorn src.api.vps_slim:app --host 0.0.0.0 --port 8001
Restart=unless-stopped

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable core-vps-slim
sudo systemctl start core-vps-slim
```

## Firewall

```bash
ufw allow 8001/tcp
ufw reload
```

## Health-Check

```bash
curl http://187.77.68.250:8001/
# Erwartet: {"status":"online","system":"ATLAS_CORE_VPS_SLIM","version":"1.0.0"}
```

## Scout-Konfiguration

Scout/atlas_conversation Failover-URL: `http://187.77.68.250:8001/webhook/forwarded_text`  
Header: `Authorization: Bearer <HA_WEBHOOK_TOKEN>`
