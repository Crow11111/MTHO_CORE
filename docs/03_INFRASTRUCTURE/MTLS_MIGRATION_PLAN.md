<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# mTLS-Migrationsplan – GQA Refactor F3 (unified-auth-mtls)

**Zweck:** Einheitliches mTLS-Schema für alle Service-to-Service-Kommunikation in CORE. Ersetzt den Wildcard-Token-Ansatz durch Zertifikats-basierte gegenseitige Authentifizierung.

**Stand:** 2026-03  
**Status:** Konzept / Planung  
**Geschützte Module:** Auth/Credentials (Stufe 1) – Umsetzung nur nach Freigabe durch Code-Sicherheitsrat.

---

## 1. Aktuelle Auth-Struktur (Ist-Zustand)

### 1.1 `src/api/auth_webhook.py`

| Funktion | Methode | Env-Variable | Verwendung |
|----------|---------|---------------|------------|
| `verify_whatsapp_auth` | Shared-Secret Header | `ATLAS_WEBHOOK_SECRET` | X-CORE-WEBHOOK-SECRET |
| `verify_ha_auth` | Bearer Token | `HA_WEBHOOK_TOKEN` | Bearer für /webhook/ha_action, /webhook/inject_text |
| `verify_oc_auth` | API-Key / Bearer | `OPENCLAW_GATEWAY_TOKEN` | X-API-Key oder Bearer für /api/oc/* |

**Positiv:** Constant-time Vergleich (`secrets.compare_digest`), keine Secrets im Code.  
**Risiko:** Token in .env; Rotation manuell; kein Identitätsnachweis (jeder mit Token = gleichberechtigt).

### 1.2 Weitere Token-Verbindungen

| Verbindung | Protokoll | Auth | Env |
|------------|-----------|------|-----|
| CORE → OpenClaw Gateway | HTTP/HTTPS | Bearer | OPENCLAW_GATEWAY_TOKEN |
| Scout/HA → OpenClaw | HTTP POST | Bearer | OPENCLAW_GATEWAY_TOKEN |
| Scout → 4D_RESONATOR (CORE) (SSH) | SSH | Passwort/Key | HA_SSH_USER, HA_SSH_PASSWORD, SSH_KEY_PATH |
| Cursor → VPS (MCP) | HTTP/SSH | (nicht dokumentiert) | MCP-Server auf VPS:8001 |
| 4D_RESONATOR (CORE) → ChromaDB (VPS) | HTTP | Keine | CHROMA_HOST, CHROMA_PORT |
| VPS SSH | SSH | Passwort/Key | VPS_USER, VPS_PASSWORD, VPS_SSH_KEY |

---

## 2. mTLS-Schema (Soll-Zustand)

### 2.1 Zertifikats-Hierarchie

```
                    ┌─────────────────────────────────────┐
                    │  CORE Root CA (self-signed)         │
                    │  CN=core-ca.local, 10 Jahre        │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Server CA      │       │  Client CA      │       │  (Reserve)       │
│  CN=core-srv   │       │  CN=core-cli   │       │                  │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
    ┌────┴────┐              ┌─────┴─────┐
    │         │              │           │
    ▼         ▼              ▼           ▼
┌───────┐ ┌───────┐    ┌─────────┐ ┌─────────┐
│CORE  │ │ MCP   │    │ cursor  │ │ oc-brain│
│ API   │ │ Server│    │ client  │ │ client  │
│(Dread)│ │(VPS)  │    │         │ │         │
└───────┘ └───────┘    └─────────┘ └─────────┘
    │         │              │           │
    │         │         ┌────┴────┐      │
    │         │         │         │      │
    ▼         ▼         ▼         ▼      ▼
┌─────────┐ ┌─────────┐
│ scout   │ │ ha      │
│ client  │ │ client  │
└─────────┘ └─────────┘
```

**Prinzip:**  
- **Root CA:** Eine zentrale CA pro CORE-Installation (oder pro Mandant).  
- **Server CA:** Signiert Server-Zertifikate (CORE API, MCP Server, OpenClaw Gateway).  
- **Client CA:** Signiert Client-Zertifikate (Cursor, Scout, OMEGA_ATTRACTOR, HA).  
- **Trennung:** Server- und Client-CA getrennt → Revocation pro Rolle möglich.

### 2.2 Zertifikats-Mapping pro Verbindung

| Verbindung | Server-Cert | Client-Cert | Port |
|------------|-------------|-------------|------|
| **Cursor → VPS (MCP)** | MCP-Server (VPS) | cursor-client | 8001 (TLS) |
| **Scout → 4D_RESONATOR (CORE)** | CORE API | scout-client | 8000 (TLS) |
| **OMEGA_ATTRACTOR → CORE API** | CORE API | oc-brain-client | 8000 (TLS) |
| **HA → CORE API** | CORE API | ha-client | 8000 (TLS) |
| **CORE → OpenClaw** | OpenClaw Gateway | core-client | 18789/443 (TLS) |
| **CORE → ChromaDB** | ChromaDB (optional) | core-client | 8000 (TLS) |

**Hinweis:** ChromaDB unterstützt mTLS nicht nativ; Option: Reverse-Proxy (z. B. Nginx) mit mTLS vor ChromaDB.

### 2.3 Subject-Namen (SAN/CN)

| Zertifikat | CN | SAN (Subject Alternative Names) |
|-------------|-----|----------------------------------|
| core-api-server | core-api.dreadnought.local | DNS:core-api.local, IP:192.168.178.x |
| mcp-server | mcp.vps.core.local | DNS:mcp.vps.core.local, IP:VPS_IP |
| openclaw-server | openclaw.vps.core.local | DNS:openclaw.vps.core.local |
| cursor-client | cursor.dreadnought.local | - |
| scout-client | scout.raspi.local | - |
| oc-brain-client | oc-brain.vps.core.local | - |
| ha-client | ha.scout.local | - |
| core-client | core.dreadnought.local | - |

---

## 3. Migrations-Schritte (Token → mTLS)

### Phase 1: Vorbereitung (ohne Produktionsänderung)

1. **CA und Zertifikate generieren**  
   - Skript: `src/scripts/generate_mtls_certs.py` (siehe Abschnitt 6)  
   - Ausgabe: `data/certs/` (nicht versionieren, .gitignore)

2. **Zertifikats-Pfade in .env dokumentieren**  
   - Neue Variablen: `MTLS_CA_CERT`, `MTLS_SERVER_CERT`, `MTLS_SERVER_KEY`, `MTLS_CLIENT_CERT`, `MTLS_CLIENT_KEY`  
   - Noch nicht aktiv nutzen

3. **Fallback-Logik in auth_webhook.py vorbereiten**  
   - Neue Funktion `verify_mtls_or_token()`: Zuerst mTLS prüfen, bei fehlendem Client-Cert → Token-Fallback

### Phase 2: Dual-Mode (mTLS + Token parallel)

4. **CORE API:** TLS aktivieren (uvicorn mit ssl_context), mTLS optional  
   - Client-Cert-Validierung: Nur wenn Request Client-Cert mitschickt  
   - Token weiterhin akzeptiert für Legacy-Clients

5. **OpenClaw Gateway:** mTLS als zusätzliche Auth-Option (wenn OpenClaw das unterstützt; sonst Nginx vor Gateway)

6. **MCP-Server:** TLS + optional mTLS (Cursor-Client-Cert)

### Phase 3: Migration pro Client

7. **Scout/HA:** Client-Cert auf Raspi deployen, HA Automation auf HTTPS+mTLS umstellen  
8. **OMEGA_ATTRACTOR:** Client-Cert in OpenClaw-Container, Requests mit Cert  
9. **Cursor:** MCP-Client mit Client-Cert konfigurieren  
10. **CORE → OpenClaw:** openclaw_client.py auf mTLS umstellen

### Phase 4: Token-Deprecation

11. **Token-Fallback deaktivieren** (konfigurierbar: `MTLS_LEGACY_TOKEN_FALLBACK=0`)  
12. **Alte Token aus .env entfernen** (nach Bestätigung aller Clients migriert)  
13. **rotate_tokens.py** anpassen oder obsolet

---

## 4. Fallback für Legacy-Clients

### 4.1 Konfiguration

```env
# .env
MTLS_LEGACY_TOKEN_FALLBACK=1   # 1 = Token weiterhin akzeptieren, 0 = nur mTLS
MTLS_REQUIRE_CLIENT_CERT=0     # 0 = optional (Fallback möglich), 1 = Pflicht
```

### 4.2 Auth-Flow (auth_webhook.py – konzeptionell)

```python
# Pseudocode – nicht direkt übernehmen
def verify_oc_auth_mtls_or_token(request):
    # 1. mTLS: Client-Cert vorhanden und von Client-CA signiert?
    if request.scope.get("transport") and has_valid_client_cert(request):
        return  # OK
    # 2. Fallback: Token (wie bisher)
    if MTLS_LEGACY_TOKEN_FALLBACK:
        verify_oc_auth(request)  # X-API-Key / Bearer
    else:
        raise HTTPException(401, "mTLS erforderlich")
```

### 4.3 Welche Clients sind „Legacy“?

| Client | Migrations-Priorität | Begründung |
|--------|----------------------|------------|
| WhatsApp Webhook | Niedrig | Externer Dienst (Meta), kein Client-Cert möglich → Token bleibt |
| HA/Scout | Mittel | Raspi kann Cert hosten; HA-Automation anpassbar |
| OMEGA_ATTRACTOR | Hoch | VPS-Container, Cert-Deploy machbar |
| Cursor | Hoch | Lokaler Client, Cert auf 4D_RESONATOR (CORE)/PC |
| ChromaDB-Zugriff | Optional | Proxy mit mTLS oder SSH-Tunnel |

**Ausnahme:** WhatsApp-Webhook (`ATLAS_WEBHOOK_SECRET`) bleibt dauerhaft Token-basiert – Meta sendet kein Client-Cert.

---

## 5. Sicherheits-Constraints (Audit-Checkliste)

- [ ] **Keine Secrets im Code** – Zertifikate nur über Pfade aus .env
- [ ] **Principle of Least Privilege** – Jeder Client-Cert nur für die nötigen Dienste
- [ ] **Gestaffelte Schutzlinien** – CA-Key offline/gesichert; Server/Client-Certs mit kurzer Laufzeit (z. B. 1 Jahr)
- [ ] **Revocation** – CRL oder OCSP vorbereiten (späte Phase)
- [ ] **Constant-time** – Zertifikatsvergleich keine Short-Circuit-Vergleiche

---

## 6. Cert-Generation-Script

Skript: `src/scripts/generate_mtls_certs.py`

```bash
python -m src.scripts.generate_mtls_certs [--output data/certs] [--days 365]
```

Erzeugt CA, Server- und Client-Zertifikate für Entwicklung und erste Tests.  
**Produktion:** CA-Key separat, ideal mit HSM oder Vault.

### 6.1 Ausgabe-Struktur

| Datei | Verwendung |
|-------|------------|
| `ca_root.pem`, `ca_root.key` | Root CA (geheim halten) |
| `ca_srv.pem`, `ca_cli.pem` | Intermediate CAs |
| `core-api.pem/.key` | CORE API Server |
| `mcp-server.pem/.key` | MCP-Server (VPS) |
| `openclaw-server.pem/.key` | OpenClaw Gateway |
| `cursor.pem/.key`, `scout.pem/.key`, etc. | Client-Zertifikate |
| `chain_server.pem` | CA-Chain für Server-Validierung |
| `chain_client.pem` | CA-Chain für Client-Validierung |

---

## 7. Referenzen

- `src/api/auth_webhook.py` – aktuelle Token-Auth
- `docs/02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md`
- `docs/02_ARCHITECTURE/ATLAS_SCHNITTSTELLEN_UND_KANAALE.md`
- `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` – Freigabe-Prozess
