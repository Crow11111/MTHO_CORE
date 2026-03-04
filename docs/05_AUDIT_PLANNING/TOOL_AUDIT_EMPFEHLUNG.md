# Tool-Audit – Security/DB/API-Prüfung (Phase 2)

**Auditor:** security-expert  
**Datum:** 2026-03-03  
**Grundlage:** Keine TOOL_AUDIT_LISTE.md vorhanden; Tool-Set aus Codebase (main.py, api/routes) abgeleitet.

---

## 1. Relevante Tools (aus Codebase)

| Tool / Endpoint | Zweck | Auth | DB-Schreibzugriff |
|----------------|------|------|--------------------|
| `POST /webhook/whatsapp` | WhatsApp → Triage/LLM/HA | Nein | Nein |
| `POST /webhook/ha_action`, `POST /webhook/inject_text` | HA Companion / Text-Injekt | Nein | Nein |
| `GET|POST /api/oc/*` (status, send, fetch, trigger_whatsapp_plan) | OpenClaw-Kanal | Nein | Nein (Fetch schreibt lokal) |
| `db_backend` (eigenes App: core_brain, knowledge_graph, …) | CRUD Collections | Nein | Ja (Chroma/PostgreSQL) |
| `atlas_knowledge` (Router existiert, **nicht in main.py**): GET search/evidence, **POST /evidence/add** | Semantik/Evidence | Nein | Ja (Chroma) |

---

## 2. Bewertung pro Tool

### 2.1 WhatsApp-Webhook (`/webhook/whatsapp`)
- **Auth:** Keine. Request-Body ungeprüft.
- **OWASP:** Kein HMAC (X-Hub-Signature-256) bei POST; jeder kann Payload an Webhook senden → Befehle/LLM/HA auslösen.
- **Bewertung:** **CONDITIONAL** – GO nur mit HMAC-Validierung des Webhook-Signatur (Meta); sonst NOGO für Produktion.

### 2.2 HA-Webhook (`/webhook/ha_action`, `/webhook/inject_text`)
- **Auth:** Keine. Beliebiger Aufrufer kann `atlas_command`/`text_input`/`inject_text` senden → HA-Services, LLM.
- **OWASP:** Injection (Text → Triage → HA call_service / LLM).
- **Bewertung:** **NOGO** – Keine Auth; mind. API-Key oder Shared-Secret (Header) erforderlich. Least Privilege: Webhook nur aus vertrauenswürdiger Quelle (HA mit Token).

### 2.3 OC-Channel (`/api/oc/*`)
- **Auth:** Keine auf Route. OPENCLAW_GATEWAY_TOKEN nur clientseitig (Outbound); schützt nicht die API.
- **Datenfluss:** /send, /fetch, /trigger_whatsapp_plan können von jedem aufgerufen werden → OC/SSH/WhatsApp auslösen.
- **Bewertung:** **NOGO** – Auth (Bearer/API-Key) erforderlich; /fetch und /trigger_whatsapp_plan besonders schützenswert.

### 2.4 db_backend (eigenes FastAPI-App)
- **Auth:** Keine. GET/POST auf core_brain, knowledge_graph, krypto_scan, osmium_roles, emotional_states, proactive_triggers.
- **DB:** Unkontrollierter Schreibzugriff auf Chroma/PostgreSQL (je nach Backend-Implementierung).
- **Bewertung:** **NOGO** – Keine ungeschützten Schreibzugriffe; Auth + wenn möglich nur intern (Bind 127.0.0.1) oder API-Key.

### 2.5 atlas_knowledge (Router, aktuell nicht in main gemountet)
- **GET /search, /evidence, /quaternary/*:** Nur Lesezugriff Chroma. Risiko: Informationsleck wenn öffentlich.
- **POST /evidence/add:** Schreibzugriff Chroma ohne Auth → unkontrollierter Evidence-Ingest.
- **Bewertung:** **NOGO** für POST /evidence/add ohne Auth. GET **CONDITIONAL** – nur hinter Auth oder intern.

---

## 3. Konsolidierte Empfehlung

| Maßnahme | Priorität |
|----------|-----------|
| Alle Webhooks und /api/oc mit Auth schützen (API-Key Header oder Bearer). | P0 |
| WhatsApp POST: HMAC (X-Hub-Signature-256) prüfen; bei Fehler 401. | P0 |
| db_backend und POST /evidence/add: Kein öffentlicher Zugriff; Auth oder nur localhost. | P0 |
| HA-Webhook: Shared-Secret/Token aus HA (z. B. Header `X-HA-Token`) validieren. | P0 |
| CORS prüfen: allow_origins nicht auf `*` in Produktion. | P1 |

**Fazit:** Kein Tool in aktueller Form **GO** für produktive Exposition ohne Auth. **Conditional GO** nur nach Umsetzung P0 (Auth + WhatsApp HMAC). Bis dahin: **NOGO** für alle genannten Endpoints außerhalb vertrauenswürdiger Umgebung.

---

## 4. Anhang: Referenzen

- ATLAS Auth: Bearer/API-Key, OpenClaw Gateway Token (Outbound).
- OWASP: Injection, Broken Access Control; Webhook-Signatur (HMAC).
- Skill: `.cursor/skills/expertise/security/SKILL.md`
