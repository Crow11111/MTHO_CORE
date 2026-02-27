# VPS-Dienste-Strategie & OpenClaw-Sandbox

**Kontext:** Der Hostinger-VPS (187.77.68.250) ist ein eigener Server – nicht nur für OpenClaw. Dienste, die auf Pi oder PC ressourcenintensiv oder wartungsintensiv sind, können hier sinnvoll ausgelagert werden. **OpenClaw muss dabei in einer Sandbox laufen** und darf keinen Zugriff auf andere Dienste oder sensible Daten auf demselben Server erhalten.

---

## 1. Welche Dienste sind Auslagerungs-Kandidaten?

| Dienst | Aktuell | Auf VPS sinnvoll? | Begründung |
|--------|---------|-------------------|------------|
| **OpenClaw** | (geplant VPS) | **Ja** | Messenger-Gateway braucht öffentliche Erreichbarkeit; läuft in **Sandbox** (siehe Abschnitt 2). |
| **ChromaDB** | Dreadnought (lokal) / optional VPS | **Ja** | Entlastet Dreadnought (NVMe/I/O); zentrale RAG-DB für ATLAS; bereits angebunden (`CHROMA_HOST`). |
| **Ollama (leichtere Modelle)** | Dreadnought (i5, GTX 3050) | **Optional** | Kleine Modelle (z. B. für Vorverarbeitung, Routing) könnten auf VPS laufen; **schweres RAG/Osmium bleibt auf Dreadnought** (Datenhoheit, Latenz). |
| **Backup-Ziel / Sync** | aktiv | **Ja** | VPS als externes Backup-Ziel (`/var/backups/atlas`); `daily_backup.py` pusht von Dreadnought per SFTP; Retention 7 Tage (Cron auf VPS). Siehe [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md). |
| **API-Proxy / Webhook-Empfang** | HA + Dreadnought | **Optional** | Öffentliche URL für Webhooks (z. B. von OpenClaw zu ATLAS); nur Weiterleitung, keine Logik. |
| **Dev-Agent / Streamlit** | Lokal (PC) | **Eher nein** | Braucht lokale Keys, Kontext, ggf. Cursor; besser auf Dreadnought. |
| **Home Assistant** | Scout (Pi) | **Nein** | Bleibt lokal (Smart Home, Latenz, Datenhoheit). |
| **Ollama (Haupt-Inferenz)** | Dreadnought | **Nein** | GPU + sensible ND-Daten bleiben auf Dreadnought. |

**Faustregel:**  
- **VPS:** Öffentlich erreichbare Dienste (OpenClaw, ggf. Webhook-Empfang), zentrale DB (Chroma), Backup-Ziel, optional leichtes Ollama.  
- **Dreadnought:** Kern-LLM, Chroma-Option lokal, Dev-Agent, alle Keys und sensiblen Daten.  
- **Scout (Pi):** HA, Edge, lokale Sensoren/WhatsApp-Webhook zu ATLAS.

---

## 2. OpenClaw-Sandbox (Pflicht)

OpenClaw verbindet sich mit externen Messengern (WhatsApp, Telegram, …) und leitet Nachrichten weiter. Er darf **keinen Zugriff** auf andere Dienste auf demselben Server haben (kein ChromaDB, kein Ollama, keine .env, keine SSH-Keys).

### 2.1 Empfohlene Maßnahmen

| Maßnahme | Beschreibung |
|----------|--------------|
| **Docker-Container** | OpenClaw ausschließlich in einem eigenen Container betreiben (offizielles Image bzw. eigenes minimales Image). Kein `--network=host`; nur definierte Ports (z. B. 18789) nach außen. |
| **Eigenes Netzwerk** | Docker-Netzwerk nur für OpenClaw; andere Dienste (Chroma, Ollama) in anderem Netzwerk oder auf localhost des Hosts. OpenClaw erhält keine IPs zu Chroma/Ollama. |
| **Unprivilegierter User** | Container läuft als nicht-root User (wenn das Image/Setup das unterstützt). |
| **Keine Volumes in sensible Bereiche** | Kein Mount von `/root`, `.env`, oder Chroma-Daten in den OpenClaw-Container. Nur Konfiguration für OpenClaw (z. B. `openclaw.json`). |
| **Firewall** | Host-Firewall: Nur nötige Ports (22 SSH, 80/443 optional, 18789 OpenClaw) von außen; intern keine Dienste von OpenClaw zu Chroma/Ollama erreichbar. |
| **Kommunikation ATLAS ↔ OpenClaw** | Nur von außen (ATLAS_CORE auf Dreadnought/PC) zum OpenClaw-Gateway (HTTPS/HTTP); OpenClaw ruft nicht zurück auf den Rest des Servers. |

### 2.2 Architektur-Skizze (VPS)

```
[Internet]
    │
    ├──► [OpenClaw-Container]  Port 18789  (Sandbox, nur dieser Dienst)
    │         │
    │         └──► Nachrichten nur an externe ATLAS-URL (z. B. Webhook auf Dreadnought/NGROK)
    │
    └──► [ChromaDB]  Port 8000  (nur von ATLAS/vertrauenswürdigen Clients)
    └──► [optional: Ollama light]  Port 11434  (nur intern oder nur für ATLAS)
```

OpenClaw hat **keine** Verbindung zu ChromaDB oder Ollama auf demselben Host; alle LLM-/RAG-Anfragen gehen von ATLAS_CORE (lokal) aus, das ggf. ChromaDB auf dem VPS per `CHROMA_HOST` anspricht.

### 2.3 Checkliste vor Go-Live

- [ ] OpenClaw läuft in eigenem Docker-Container (kein Zugriff auf Host-Dateisystem außer OpenClaw-Config).
- [ ] Kein gemeinsames Docker-Netzwerk mit ChromaDB/Ollama; oder Chroma/Ollama nicht im selben Netzwerk wie OpenClaw.
- [ ] Firewall: Keine eingehenden Verbindungen von OpenClaw-Container zu anderen Ports auf dem Host.
- [ ] ATLAS_CORE ruft OpenClaw-Gateway von außen auf (Token in .env); OpenClaw leitet nur an konfigurierte Webhook-URLs weiter.

---

## 3. Bei Hostinger umsetzen (konkrete Schritte)

Folgende Dinge sind **auf dem VPS (187.77.68.250)** umzusetzen, damit die Dienste aus Abschnitt 1 laufen und OpenClaw sandboxed bleibt.

### 3.1 Basis (einmalig)

| Schritt | Aktion |
|--------|--------|
| SSH | `ssh root@187.77.68.250` (Zugang aus ATLAS .env: VPS_HOST, VPS_USER, VPS_PASSWORD). |
| Firewall | Nur nötige Ports von außen öffnen: 22 (SSH), 80/443 (optional), 18789 (OpenClaw), 8000 (ChromaDB nur wenn von außen nötig). Chroma/Ollama ideal nur localhost oder über SSH-Tunnel. |
| Docker | Falls noch nicht installiert: Docker installieren (z. B. `curl -fsSL https://get.docker.com | sh`), damit OpenClaw und ggf. Chroma im Container laufen. |

### 3.2 OpenClaw (in Sandbox)

| Schritt | Aktion |
|--------|--------|
| 1 | Eigenes Docker-Netzwerk anlegen: `docker network create openclaw_net` (nur für OpenClaw). |
| 2 | OpenClaw-Container **ohne** Mount von `/root` oder Host-Config außer der OpenClaw-Konfiguration starten. Nur Port 18789 nach außen mappen. Kein `--network=host`. |
| 3 | OpenClaw so konfigurieren, dass er nur an konfigurierte Webhook-URLs (z. B. ATLAS-Core-URL/NGROK) weiterleitet – keine internen Host-URLs (kein localhost:8000 für Chroma, kein localhost:11434). |
| 4 | In ATLAS_CORE .env: `OPENCLAW_GATEWAY_TOKEN` und `VPS_HOST` gesetzt; Test mit `check_gateway()` aus `openclaw_client` sobald OpenClaw läuft. |

### 3.3 ChromaDB

| Schritt | Aktion |
|--------|--------|
| 1 | Chroma läuft im Container `chroma-atlas`; **gebunden an 127.0.0.1:8000** (nicht öffentlich). |
| 2 | **Zugriff von außen:** Nur per SSH-Tunnel, z. B. `ssh -L 8000:127.0.0.1:8000 root@VPS_HOST`. Dann in .env: `CHROMA_HOST=localhost`, `CHROMA_PORT=8000`. |
| 3 | Ingest von Dreadnought aus (wenn Tunnel aktiv): `python src/scripts/ingest_nd_insights_to_chroma.py`. |

### 3.4 Backup-Ziel (aktiv)

| Schritt | Aktion |
|--------|--------|
| 1 | Verzeichnis `/var/backups/atlas` wird von `setup_vps_hostinger.py` angelegt; Cron löscht Backups älter als 7 Tage. |
| 2 | **daily_backup.py** (auf Dreadnought) pusht täglich per SFTP; Aufruf per Task Scheduler (Windows) oder cron. Siehe [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md). |
| 3 | Der VPS pullt nicht; nur Push von ATLAS_CORE aus. |

### 3.5 Optional: leichtes Ollama, Webhook-Proxy

- **Ollama (leicht):** Nur wenn gewünscht – kleines Modell auf dem VPS installieren, Port 11434 nur für ATLAS-IP oder über Tunnel erreichbar halten. Schweres RAG/Osmium bleibt auf Dreadnought.
- **Webhook-Proxy:** Nginx/Caddy auf dem VPS, der nur bestimmte Pfade (z. B. `/webhook/openclaw`) an deine ATLAS-URL (NGROK oder DynDNS) weiterleitet; keine Logik auf dem VPS.

### 3.6 Übersicht: Ports auf dem VPS

| Port | Dienst | Von außen? |
|------|--------|-------------|
| 22 | SSH | Ja (für Admin) |
| 18789 | OpenClaw | Ja (Messenger-Gateway) |
| 8000 | ChromaDB | Nur 127.0.0.1 auf VPS; Zugriff von außen nur per SSH-Tunnel |
| 80/443 | Nginx/Caddy (optional) | Optional (Webhook-Proxy, Let’s Encrypt) |

---

## 4. Referenzen

- **Schnittstellen:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](DEV_AGENT_UND_SCHNITTSTELLEN.md) (OpenClaw, ChromaDB, Go2RTC, .env).
- **Hardware:** [01_ARCHITEKTUR_HARDWARE_OSMIUM.md](../data/antigravity_docs_osmium/01_ARCHITEKTUR_HARDWARE_OSMIUM.md) (Dreadnought, Scout).
- **OpenClaw Docs:** https://docs.openclaw.ai/
- **Go2RTC (Kamera PC):** [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md).
