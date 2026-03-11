<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Session 2026-03-04: MTHO Voice Assistant Integration

**Datum:** 2026-03-04
**Scope:** Voice Assistant Pipeline, GQA Refactor, Home Assistant Integration

---

## 1. Zusammenfassung

Diese Session umfasste die vollständige Integration des MTHO Voice Assistant Systems mit Home Assistant. Kernpunkte:

- **GQA (Gravitational Query Architecture) Refactor** – 8 Tasks für Wuji-native Architektur
- **Custom HA Conversation Agent** – Native Integration in die HA Assist-Pipeline
- **Scout-Konfiguration** – Samba/SSH-Zugriff, Wyoming-Stack (Whisper, Piper, openWakeWord)
- **MTHO API Server** – Port 8088 auf 4D_RESONATOR (MTHO_CORE), Webhook-Authentifizierung

---

## 2. Architektur-Übersicht (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MTHO Voice Assistant System                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────────────────────────────────────────┐│
│   │     SCOUT       │    │                   DREADNOUGHT                       ││
│   │ (Raspi 5 / HA)  │    │                (MTHO_CORE Host)                    ││
│   │ 192.168.178.54  │    │               192.168.178.110                       ││
│   ├─────────────────┤    ├─────────────────────────────────────────────────────┤│
│   │                 │    │                                                     ││
│   │ openWakeWord    │    │  MTHO API (Port 8088)                              ││
│   │ "hey atlas"     │    │  ├── /webhook/inject_text (Conversation Agent)     ││
│   │       │         │    │  ├── /webhook/assist (TTS-triggering)              ││
│   │       ▼         │    │  └── /webhook/ha_action (Companion App)            ││
│   │ Whisper STT     │    │           │                                         ││
│   │       │         │    │           ▼                                         ││
│   │       ▼         │    │  ┌───────────────────────────────────────┐          ││
│   │ MTHO Conver-   │────┼─►│ scout_direct_handler.process_text()  │          ││
│   │ sation Agent    │    │  │   ├── smart_command_parser (NL→HAAction)        ││
│   │       │         │    │  │   ├── Hugin Triage (command/chat/deep)          ││
│   │       ▼         │    │  │   └── OMEGA_ATTRACTOR Fallback (VPS)                   ││
│   │ Piper TTS       │◄───┼──│           │                                      ││
│   │       │         │    │  └───────────┼───────────────────────────┘          ││
│   │       ▼         │    │              ▼                                      ││
│   │ Mini-Speaker    │    │  HomeAssistantClient.call_service()                ││
│   │ (media_player.  │◄───┼──────────────────────────────────────────          ││
│   │  schreibtisch)  │    │                                                     ││
│   │                 │    │                                                     ││
│   └─────────────────┘    └─────────────────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

    Datenfluss:
    ───────────
    1. User: "Hey MTHO, Regal 80% Helligkeit"
    2. openWakeWord → Wake Word erkannt
    3. Whisper STT → "Regal 80% Helligkeit"
    4. MTHO Conversation Agent → POST /webhook/inject_text
    5. scout_direct_handler → smart_command_parser
       → HAAction(light, turn_on, light.regal, {brightness_pct: 80})
    6. HAClient.call_service() → Licht gesteuert
    7. Reply: "Befehl ausgeführt: turn_on auf light.regal"
    8. Piper TTS → Sprachausgabe auf Mini-Speaker
```

---

## 3. Implementierte Komponenten

### 3.1 Custom Home Assistant Integration

| Datei | Funktion |
|-------|----------|
| `ha_integrations/atlas_conversation/__init__.py` | Entry Setup, Agent-Registrierung |
| `ha_integrations/atlas_conversation/agent.py` | `AtlasConversationAgent` – HA Conversation Protocol |
| `ha_integrations/atlas_conversation/api.py` | `AtlasApiClient` – HTTP-Client für MTHO API |
| `ha_integrations/atlas_conversation/config_flow.py` | UI-Config Flow für Integration |
| `ha_integrations/atlas_conversation/const.py` | Domain, Defaults |
| `ha_integrations/atlas_conversation/manifest.json` | HA Integration Manifest |
| `ha_integrations/atlas_conversation/README.md` | Installationsanleitung |

### 3.2 MTHO API Endpoints (Webhook-Routes)

| Endpoint | Datei | Zweck |
|----------|-------|-------|
| `POST /webhook/inject_text` | `src/api/routes/ha_webhook.py` | Text von Conversation Agent |
| `POST /webhook/assist` | `src/api/routes/ha_webhook.py` | Assist-Pipeline + TTS-Trigger |
| `POST /webhook/ha_action` | `src/api/routes/ha_webhook.py` | Companion App Events |
| `POST /webhook/forwarded_text` | `src/api/routes/ha_webhook.py` | VPS-Fallback Route |

### 3.3 Voice Processing Pipeline

| Modul | Funktion |
|-------|----------|
| `src/services/scout_direct_handler.py` | Zentrale Triage: Command/Chat/Deep |
| `src/voice/smart_command_parser.py` | NL → HAAction (Pattern + LLM-Fallback) |
| `src/voice/tts_dispatcher.py` | TTS-Routing: mini, ElevenLabs, Piper |
| `src/voice/play_sound.py` | Audio-Dateien auf Mini-Speaker |
| `src/connectors/home_assistant.py` | Async HA-Client (call_service, get_states) |
| `src/network/ha_client.py` | Sync HA-Client (call_service, send_whatsapp) |

### 3.4 GQA Refactor Tasks (8 Tasks)

| Task | Beschreibung | Status |
|------|--------------|--------|
| F2 | Scout-Direct-Mode Env-Flag | ✅ |
| F2 | scout_direct_handler.py | ✅ |
| F2 | VPS-Fallback Route (/forwarded_text) | ✅ |
| F13 | Entry Adapter (normalize_request) | ✅ |
| Ring-0 | Hugin Input-Triage | ✅ |
| Ring-0 | Munin Context Injection | ✅ |
| Ring-1 | Perf: asyncio.to_thread für Sync-Calls | ✅ |
| – | MTHO Conversation HA Integration | ✅ |

---

## 4. Konfigurationswerte

### 4.1 Netzwerk

| Host | IP | Rolle |
|------|----|-------|
| **4D_RESONATOR (MTHO_CORE)** | `192.168.178.110` | MTHO_CORE API Server |
| **Scout** | `192.168.178.54` | Home Assistant (Raspi 5) |
| **Mini-Speaker** | `media_player.schreibtisch` | TTS-Ausgabe |

### 4.2 Ports

| Service | Port | Host |
|---------|------|------|
| MTHO API | `8088` | 4D_RESONATOR (MTHO_CORE) |
| HA REST API | `8123` (HTTPS) | Scout |
| TTS Stream | `8002` | 4D_RESONATOR (MTHO_CORE) (MTHO_HOST_IP) |

### 4.3 Umgebungsvariablen (.env auf 4D_RESONATOR (MTHO_CORE))

| Variable | Beschreibung | Hinweis |
|----------|--------------|---------|
| `SCOUT_DIRECT_MODE` | Scout-Direct-Handler aktiv | `true` für lokale HA-Calls |
| `HASS_URL` / `HA_URL` | Home Assistant URL | Scout-IP mit Port 8123 |
| `HASS_TOKEN` / `HA_TOKEN` | HA Long-Lived Token | Aus HA Profil |
| `HA_WEBHOOK_TOKEN` | Bearer für /webhook/* Endpoints | Zufällig generiert |
| `TTS_TARGET` | TTS-Ziel | `mini`, `elevenlabs`, `both` |
| `TTS_CONFIRMATION_ENTITY` | media_player für TTS | `media_player.schreibtisch` |
| `ELEVENLABS_API_KEY` | ElevenLabs API | Optional |
| `MTHO_HOST_IP` | IP für Audio-Stream | `192.168.178.110` |
| `TTS_STREAM_PORT` | HTTP-Port für Audio-Stream | `8002` |

### 4.4 HA-Konfiguration (Scout)

**Geheimnisse (secrets.yaml):**
```yaml
atlas_api_url: "http://192.168.178.110:8088"
atlas_webhook_token: "<HA_WEBHOOK_TOKEN aus .env>"
```

**rest_command (configuration.yaml):**
```yaml
rest_command:
  atlas_assist:
    url: "{{ atlas_api_url }}/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer {{ atlas_webhook_token }}"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

### 4.5 Wyoming-Stack Add-ons (Scout)

| Add-on | Zweck | Status |
|--------|-------|--------|
| **Whisper** | Speech-to-Text | ✅ Installiert |
| **openWakeWord** | Wake-Word-Erkennung | ✅ Installiert |
| **Piper** | Text-to-Speech | ✅ Installiert |

---

## 5. Integration Deployment

### 5.1 Installation der MTHO Conversation Integration

1. **Dateien kopieren:**
   ```bash
   # Von 4D_RESONATOR (MTHO_CORE) (Samba/SSH):
   scp -r ha_integrations/atlas_conversation/ pi@192.168.178.54:/config/custom_components/
   ```

2. **Home Assistant neu starten**

3. **Integration hinzufügen:**
   - Einstellungen → Geräte & Dienste → Integration hinzufügen
   - "MTHO Conversation" suchen
   - MTHO API URL: `http://192.168.178.110:8088`
   - Bearer Token: `<HA_WEBHOOK_TOKEN>`

### 5.2 Assist-Pipeline konfigurieren

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** "MTHO"
3. **Conversation Agent:** MTHO Conversation
4. **Speech-to-Text:** Whisper
5. **Text-to-Speech:** Piper
6. **Wake Word:** openWakeWord ("hey atlas")

---

## 6. Test-Prozeduren

### 6.1 API direkt testen

```bash
curl -X POST http://192.168.178.110:8088/webhook/inject_text \
  -H "Authorization: Bearer <HA_WEBHOOK_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

Erwartete Antwort:
```json
{"status":"ok","action":"voice_processed","reply":"Befehl ausgeführt: turn_on auf light.regal"}
```

### 6.2 HA Integration testen

1. **Entwicklerwerkzeuge → Dienste**
2. Service: `conversation.process`
3. Daten: `text: "Schalte das Licht an"`
4. Agent ID: MTHO Conversation Entity

### 6.3 Voice-Pipeline E2E

1. Wake Word sagen: "Hey MTHO"
2. Befehl sprechen: "Schalte das Regal auf 80% Helligkeit"
3. Piper spricht Antwort

---

## 7. Offene Punkte / Next Steps

### Priorität 1 (Kurzfristig)

- [ ] **Custom Wake-Word Model** – "hey atlas" oder "atlas" trainieren (openWakeWord)
- [ ] **Entity Resolution** – `context["entities"]` bei Conversation Agent übergeben
- [ ] **Error-Handling** – Retry-Logik bei HA-Verbindungsabbruch

### Priorität 2 (Mittelfristig)

- [ ] **ElevenLabs Streaming** – Latenz für komplexe Antworten reduzieren
- [ ] **Feedback-Sound** – NASA Mission Complete nach Command-Ausführung
- [ ] **VPS-Fallback Testing** – Scout → VPS Route validieren

### Priorität 3 (Langfristig)

- [ ] **HACS-Repository** – MTHO Conversation als Custom Repo verfügbar machen
- [ ] **Multi-Room Audio** – TTS auf mehreren Speakern je nach Raum
- [ ] **Presence-Based Context** – Nutzerposition in Smart-Parser einbeziehen

---

## 8. Referenzen

| Dokument | Pfad |
|----------|------|
| Voice Architecture | `docs/02_ARCHITECTURE/MTHO_VOICE_ASSISTANT_ARCHITECTURE.md` |
| Scout Pipeline | `docs/03_INFRASTRUCTURE/SCOUT_ASSIST_PIPELINE.md` |
| Integration README | `ha_integrations/atlas_conversation/README.md` |
| Webhook Routes | `src/api/routes/ha_webhook.py` |
| Scout Handler | `src/services/scout_direct_handler.py` |
| Smart Parser | `src/voice/smart_command_parser.py` |
| TTS Dispatcher | `src/voice/tts_dispatcher.py` |
| HA Client | `src/connectors/home_assistant.py` |

---

## 9. Changelog

| Zeit | Änderung |
|------|----------|
| 09:00 | Session Start, GQA Refactor Planning |
| 10:30 | scout_direct_handler.py implementiert |
| 12:00 | MTHO Conversation HA Integration erstellt |
| 14:00 | Samba/SSH-Zugriff auf Scout konfiguriert |
| 15:30 | Integration auf Scout deployed |
| 16:00 | MTHO API Server auf Port 8088 gestartet |
| 17:00 | Assist-Pipeline konfiguriert und getestet |
| 18:00 | Session-Dokumentation erstellt |

---

*Erstellt: 2026-03-04*
*Autor: MTHO Orchestrator (Session-Dokumentation)*
