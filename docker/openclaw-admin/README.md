# OpenClaw Admin (Gehirn)

Native Docker-Compose-Installation für die **Admin-Instanz** (alle API-Keys, Gemini 3.1 Pro, WhatsApp).

- **Deployment:** Siehe `src/scripts/deploy_openclaw_admin_vps.py` (legt `data/` an, schreibt Config, startet Container).
- **Architektur:** [docs/OPENCLAW_ADMIN_ARCHITEKTUR.md](../../docs/OPENCLAW_ADMIN_ARCHITEKTUR.md).

Nach dem Deploy: Gateway auf Port 18789. In ATLAS .env: `OPENCLAW_GATEWAY_TOKEN`, für Admin-VPS ggf. `OPENCLAW_ADMIN_VPS_HOST` und Port 18789.
