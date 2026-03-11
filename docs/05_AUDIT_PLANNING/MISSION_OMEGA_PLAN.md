<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# MISSION OMEGA: Autonome Intelligenz für MTHO

**Status:** PLAN | **Datum:** 2026-03-05  
**Referenz:** MTHO_AGENT_NIGHT_SHIFT_FAILOVER.md, MTHO_AGI_ARCHITECTURE, AUTONOMOUS_VISION_LOOP

---

## 1. Leitprinzipien

| # | Prinzip | Bedeutung |
|---|---------|-----------|
| 1 | **Keine Kernfunktionen auf 4D_RESONATOR (MTHO_CORE)** | Scout + VPS/Brain sind das Backbone. 4D_RESONATOR (MTHO_CORE) = Turbo/Dev, nicht kritisch. |
| 2 | **Failover: 4D_RESONATOR (MTHO_CORE) aus → VPS übernimmt** | Zero-Downtime. Scout routet transparent auf VPS, wenn 4D_RESONATOR (MTHO_CORE) nicht antwortet. |
| 3 | **Reaktive Abläufe** | Sensoren triggern Aktionen. Event → Triage → Aktion. |
| 4 | **Proaktive Sensorik** | System erkennt Muster, handelt vorausschauend (Vision Loop, Präsenz-Inferenz). |
| 5 | **Fühlen und Denken** | Kontext (Wuji-Feld) und Reasoning (OMEGA_ATTRACTOR) fließen in die Kette ein. |

---

## 2. Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           MISSION OMEGA – AUTONOME INTELLIGENZ                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│   SENSORIK (Scout)                    BACKBONE (VPS/OMEGA_ATTRACTOR)              AKTIONEN      │
│   ─────────────────                   ───────────────────────             ───────      │
│                                                                                          │
│   ┌──────────────┐                    ┌─────────────────────────────┐                   │
│   │ openWakeWord │                    │  OMEGA_ATTRACTOR (OpenClaw)         │     ┌──────────┐  │
│   │ Whisper STT  │                    │  - Deep Reasoning (Gemini)   │     │ HA       │  │
│   │ Assist Mic   │                    │  - Kontext-Aggregation      │     │ Services │  │
│   └──────┬───────┘                    │  - WhatsApp, OMEGA_ATTRACTOR Council-Submissions│     └────▲─────┘  │
│          │                            └──────────────┬──────────────┘            │       │
│          ▼                                           │                           │       │
│   ┌──────────────┐                    ┌──────────────▼──────────────┐            │       │
│   │ MX Brio      │                    │  ChromaDB (Wuji-Feld)       │            │       │
│   │ Vision Loop  │                    │  - events, insights         │            │       │
│   │ (go2rtc)     │                    │  - wuji_field, session_logs  │            │       │
│   └──────┬───────┘                    │  - core_directives         │            │       │
│          │                            └─────────────────────────────┘            │       │
│          │                                                                       │       │
│   ┌──────▼──────────────────────────────────────────────────────────────────────▼───┐  │
│   │  SCOUT (Raspi 5 / HA OS)                                                          │  │
│   │  - MTHO Conversation Integration (Failover: 4D_RESONATOR (MTHO_CORE) → VPS)                  │  │
│   │  - scout_direct_handler: Smart Parser, Triage, HA-Calls                            │  │
│   │  - Lokale Aktionen (Licht, etc.) direkt via HAClient                              │  │
│   │  - Deep Reasoning → OMEGA_ATTRACTOR (VPS)                                                │  │
│   └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                          │                                               │
│                                          │ Failover wenn 4D_RESONATOR (MTHO_CORE) OFF                 │
│   ┌──────────────────────────────────────▼──────────────────────────────────────────┐   │
│   │  DREADNOUGHT (192.168.178.20) – NUR TURBO/DEV                                   │   │
│   │  - MTHO API (webhook/inject_text) – optional, nicht kritisch                    │   │
│   │  - Lokales Heavy (Gemini) als Turbo bei Bedarf                                   │   │
│   │  - Vision Daemon (kann auf Scout migriert werden)                                  │   │
│   └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Komponenten-Detail

### 3.1 Scout (HA OS, Raspi 5) – Sinne & lokale Aktionen

| Komponente | Funktion | Datenfluss |
|------------|----------|------------|
| **Assist Pipeline** | openWakeWord → Whisper STT → MTHO Conversation Agent | Audio → Text |
| **MTHO Conversation** | Custom Integration, POST an 4D_RESONATOR (MTHO_CORE) oder VPS | Text → API |
| **scout_direct_handler** | Triage, Smart Parser, HA-Calls, OMEGA_ATTRACTOR | Text → Aktion |
| **MX Brio (Assist Mic)** | Mikrofon für Voice | Audio-Stream |
| **go2rtc** | RTSP-Stream für Vision (Brio Kamera) | Video → Vision Daemon |
| **HAClient** | Licht, Geräte, TTS auf Mini | MTHO → HA Services |

**Scout ist immer online.** Er führt lokale Befehle aus und leitet Deep Reasoning an VPS.

### 3.2 4D_RESONATOR (MTHO_CORE) – NUR Turbo/Dev

| Komponente | Funktion | Kritikalität |
|------------|----------|--------------|
| **MTHO API** | /webhook/inject_text, /webhook/assist | Optional – Failover auf VPS |
| **Lokales Gemini** | invoke_heavy_reasoning | Turbo bei Dev-Sessions |
| **Vision Daemon** | Motion → Snapshot → Gemini Vision | Kann auf Scout migriert werden |

**4D_RESONATOR (MTHO_CORE) aus = kein Problem.** Scout routet an VPS.

### 3.3 VPS / OMEGA_ATTRACTOR – Backbone

| Komponente | Funktion | Datenfluss |
|------------|----------|------------|
| **MTHO API (Slim)** | /webhook/forwarded_text | Scout → VPS bei 4D_RESONATOR (MTHO_CORE) OFF |
| **OpenClaw Gateway** | POST /v1/responses | Deep Reasoning, WhatsApp |
| **ChromaDB** | Wuji-Feld, events, insights | Kontext für alle Agents |
| **OMEGA_ATTRACTOR (Gemini)** | Deep Reasoning, Kontext-Aggregation | Text → Antwort |

**VPS ist das Rückgrat.** ChromaDB liegt hier (oder per SSH-Tunnel erreichbar).

---

## 4. Datenflüsse

### 4.1 Reaktiv: Voice → Aktion

```
User: "Hey MTHO, Regal 80%"
    │
    ▼
openWakeWord (Scout) → Whisper STT
    │
    ▼
MTHO Conversation Agent
    │
    ├─► 4D_RESONATOR (MTHO_CORE) /webhook/inject_text (wenn erreichbar, Timeout 2s)
    │       │
    │       └─► scout_direct_handler.process_text()
    │               ├─► Smart Parser → HA light.turn_on(regal, brightness=80)
    │               └─► TTS auf Mini
    │
    └─► VPS /webhook/forwarded_text (Failover)
            │
            └─► _forwarded_text_pipeline()
                    ├─► HAClient (HASS_URL → Scout via Tunnel) → light.turn_on
                    └─► TTS via HA oder direkt
```

### 4.2 Reaktiv: Deep Reasoning

```
User: "Was denkst du über Monotropismus?"
    │
    ▼
scout_direct_handler (command path übersprungen)
    │
    ▼
Triage: deep_reasoning
    │
    ├─► OMEGA_ATTRACTOR (VPS) send_message_to_agent()  [PRIMÄR]
    │       │
    │       └─► OpenClaw nutzt ChromaDB (Wuji) für Kontext
    │
    └─► Lokales Gemini (4D_RESONATOR (MTHO_CORE)) [FALLBACK wenn OC nicht erreichbar]
            │
            └─► Munin: inject_context_for_agent() → Wuji-Feld aus ChromaDB
```

### 4.3 Proaktiv: Vision Loop

```
MX Brio (go2rtc) → atlas_vision_daemon
    │
    ▼
Motion Detection (Frame-Diff, Threshold)
    │
    ▼
Cooldown abgelaufen? → Snapshot
    │
    ▼
Gemini Vision API: "Beschreibe prägnant, was passiert"
    │
    ▼
ChromaDB: add_wuji_observation(document, metadata)
    │
    └─► Kontext für spätere Anfragen (inject_context_for_agent)
```

**Standort Vision Daemon:** Aktuell 4D_RESONATOR (MTHO_CORE). Ziel: Scout (Raspi 5) oder dedizierter Vision-Node, damit 4D_RESONATOR (MTHO_CORE) aus bleiben kann.

### 4.4 Proaktiv: Sensor-Events → OMEGA_ATTRACTOR

```
Tapo C52A (Motion) / andere Sensoren
    │
    ▼
MQTT → Scout (HA)
    │
    ▼
HA Automation: Triage (Nacht? Safe? Repetitiv?)
    │
    ▼
Wenn nicht trivial → POST https://VPS/v1/responses
    │
    └─► OMEGA_ATTRACTOR: Event loggen, ggf. WhatsApp-Eskalation
```

---

## 5. Kontext und Reasoning (Fühlen & Denken)

### 5.1 Wo kommt Kontext her?

| Quelle | Collection | Nutzung |
|--------|------------|---------|
| **Vision Daemon** | wuji_field | "Person betritt Raum", "Licht an" |
| **Session Logs** | session_logs | Vorherige Dialoge |
| **Core Directives** | core_directives | Ring-0 Regeln |
| **Simulation Evidence** | simulation_evidence | GTAC/MTHO, Indizien |
| **Events** | events | Sensor-Events (Motion, etc.) |
| **Insights** | insights | Destillierte Erkenntnisse |

### 5.2 Wie fließt Kontext in die Kette?

```
                    ┌─────────────────────────────────────┐
                    │  ChromaDB (VPS oder per Tunnel)      │
                    │  wuji_field, session_logs, events    │
                    └────────────────┬────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│ Munin           │     │ OMEGA_ATTRACTOR           │     │ Vision Daemon       │
│ inject_context  │     │ (OpenClaw Tools)   │     │ add_wuji_observation │
│ _for_agent()    │     │ Kontext aus        │     │ (Schreibt Kontext)   │
└────────┬────────┘     │ Workspace/Chroma   │     └─────────────────────┘
         │              └─────────┬───────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  System-Prompt-Erweiterung                                        │
│  "## Relevanter Kontext (Wuji-Feld)\n" + wuji_ctx                │
│  → Gemini/OMEGA_ATTRACTOR erhält semantisch relevante Fakten             │
└─────────────────────────────────────────────────────────────────┘
```

**Ablauf:**
1. User fragt: "Warum ist es gerade so hell?"
2. `inject_context_for_agent("Warum ist es gerade so hell?", n_results=3)` → ChromaDB-Query
3. Relevante Einträge (z.B. "Licht Regal 80%", "Person hat Licht angemacht") werden als Markdown zurückgegeben
4. System-Prompt wird erweitert → LLM antwortet kontextbewusst

### 5.3 Semantic Drift Veto (Munin)

- `check_semantic_drift(wuji_ctx, reply)` prüft, ob die Antwort vom Kontext abdriftet
- Bei Veto: `apply_veto()` → z_widerstand erhöht, ggf. Antwort blockieren

---

## 6. Failover-Detail

### 6.1 atlas_conversation (HA Integration)

Bereits implementiert (api.py):

1. **Versuch 1:** POST an `base_url` (4D_RESONATOR (MTHO_CORE)) `/webhook/inject_text`
   - Timeout: `FAILOVER_TIMEOUT` (z.B. 2s connect)
2. **Bei Timeout/Error:** POST an `fallback_url` (VPS) `/webhook/forwarded_text`
3. Gleiche Payload: `{"text": "..."}`

### 6.2 VPS-Bereitschaft

Der VPS muss bereit sein:

| Endpoint | Erforderlich | Status |
|----------|--------------|--------|
| `/webhook/forwarded_text` | Ja | MTHO API auf VPS (oder Proxy) |
| ChromaDB-Zugriff | Ja | CHROMA_HOST auf VPS oder Tunnel |
| HASS_URL | Ja | Zeigt auf Scout (Nabu Casa/Tunnel) für HA-Calls |
| Munin/Wuji | Ja | inject_context_for_agent nutzt ChromaDB |

### 6.3 State-Sync (Wuji-Feld)

- ChromaDB liegt auf VPS (oder zentral)
- 4D_RESONATOR (MTHO_CORE) nutzt bei lokalem Chroma: `CHROMA_LOCAL_PATH` oder SSH-Tunnel zu VPS
- **Empfehlung:** ChromaDB nur auf VPS. 4D_RESONATOR (MTHO_CORE) und Scout-Requests (via VPS) nutzen dieselbe DB.
- `sync_core_directives_to_vps.py` / `migrate_to_context_field.py` für Direktiven-Sync

---

## 7. Implementierungs-Roadmap

### Phase 1: Failover absichern (bereits teilweise umgesetzt)

- [x] atlas_conversation: base_url + fallback_url, Lazy Failover
- [ ] VPS: MTHO API mit /webhook/forwarded_text deployen (falls nicht vorhanden)
- [ ] VPS: HASS_URL auf Scout (Tunnel) konfigurieren
- [ ] ChromaDB: Einheitlich auf VPS, 4D_RESONATOR (MTHO_CORE) per Tunnel

### Phase 2: Vision auf Scout migrieren

- [ ] atlas_vision_daemon auf Scout (Raspi 5) oder Pi 4B als Vision-Node
- [ ] go2rtc auf Scout für Brio-Stream
- [ ] Gemini API Key auf Scout (oder Vision-Node) für Kognition
- [ ] ChromaDB: add_wuji_observation von Vision-Node aus (VPS-Chroma)

### Phase 3: Proaktive Sensorik

- [ ] HA Automation: Motion/Präsenz → Triage → POST an VPS /v1/responses
- [ ] OMEGA_ATTRACTOR: Event-Handler für Scout-Events (dreadnought_pending, Eskalation)
- [ ] ChromaDB: events-Collection befüllen

### Phase 4: Mustererkennung & Vorausschau

- [ ] Predictive Matrix (action_log, ex_post_delta) auf VPS
- [ ] Pattern-Detection: Wiederkehrende Events → automatische Aktionen
- [ ] Evolution Request: Hardware-Eskalation bei Limits (MTHO_AGI_ARCHITECTURE)

---

## 8. Konfigurations-Checkliste

### Scout (HA)

| Variable | Wert | Zweck |
|----------|------|-------|
| atlas_api_url | http://192.168.178.20:8000 | 4D_RESONATOR (MTHO_CORE) (Primary) |
| atlas_fallback_url | https://187.77.68.250/... | VPS (Failover) |
| atlas_webhook_token | HA_WEBHOOK_TOKEN | Auth |

### VPS (MTHO API)

| Variable | Wert | Zweck |
|----------|------|-------|
| HASS_URL | https://... (Nabu Casa) | Scout-HA für Services |
| HASS_TOKEN | Long-Lived Token | HA-Auth |
| CHROMA_HOST | 127.0.0.1 (lokal im Container) | ChromaDB |
| HA_WEBHOOK_TOKEN | Wie Scout | Webhook-Auth |

### 4D_RESONATOR (MTHO_CORE)

| Variable | Wert | Zweck |
|----------|------|-------|
| CHROMA_HOST | localhost (Tunnel) | ChromaDB via SSH |
| SCOUT_DIRECT_MODE | true | scout_direct_handler aktiv |

---

## 9. Referenzen

- `docs/05_AUDIT_PLANNING/GHOST_AGENT_NIGHT_SHIFT_FAILOVER.md` – Failover-Spec
- `docs/02_ARCHITECTURE/MTHO_VOICE_ASSISTANT_ARCHITECTURE.md` – Voice-Pipeline
- `docs/02_ARCHITECTURE/MTHO_AGI_ARCHITECTURE.md` – Sensor → Brain
- `docs/02_ARCHITECTURE/AUTONOMOUS_VISION_LOOP.md` – Vision Daemon
- `docs/02_ARCHITECTURE/MTHO_SCHNITTSTELLEN_UND_KANAALE.md` – Kanäle
- `docs/02_ARCHITECTURE/MTHO_CHROMADB_SCHEMA.md` – Collections
- `docs/03_INFRASTRUCTURE/SCOUT_ASSIST_PIPELINE.md` – HA-Setup
- `src/services/scout_direct_handler.py` – Triage, OMEGA_ATTRACTOR, VPS-Fallback
- `ha_integrations/atlas_conversation/api.py` – Failover-Logik

---

*Erstellt: 2026-03-05 | MISSION OMEGA – Autonome Intelligenz für MTHO*
