<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Voice Assistant – Architektur

**Stand:** 2026-03-04

---

## 1. Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORE Voice Assistant                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Wyoming (HA)          │  CORE                    │  Output            │
│  ─────────────         │  ───────────                    │  ──────            │
│  openWakeWord          │  scout_direct_handler          │  TTS               │
│  Whisper STT            │  ├─ smart_command_parser      │  ├─ mini (HA TTS)  │
│  Piper TTS (optional)   │  ├─ Telemetry-Injector/Context-Injector Triage        │  ├─ ElevenLabs     │
│                         │  └─ OMEGA_ATTRACTOR (Deep Reasoning)  │  └─ Piper Fallback │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Datenfluss: Wake Word → Antwort

```
User: "Hey CORE, Regal 80% Helligkeit"
         │
         ▼
┌─────────────────────┐
│ openWakeWord        │  Wake Word erkannt
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ Whisper STT         │  Transkription: "Regal 80% Helligkeit"
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ CORE Conversation  │  HA Custom Agent → POST /webhook/inject_text
│ (ha_integrations)    │  ODER rest_command.atlas_assist → /webhook/assist
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ scout_direct_handler │  process_text(text, context)
│ process_text()      │  SCOUT_DIRECT_MODE=true
└─────────┬───────────┘
          │
          ├─► smart_command_parser.parse_command()
          │   → HAAction(light, turn_on, light.regal, {brightness_pct: 80})
          │   → HAClient.call_service()
          │
          ├─► [Fallback] Telemetry-Injector Triage → command/turn_on/turn_off
          │
          └─► [Deep Reasoning] OMEGA_ATTRACTOR / lokales Gemini
          │
          ▼
┌─────────────────────┐
│ reply               │  "Befehl ausgeführt: turn_on auf light.regal"
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ TTS                 │  dispatch_tts(reply, target=TTS_TARGET)
│                     │  target: mini | elevenlabs | elevenlabs_stream | both
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ Mini-Speaker        │  media_player.schreibtisch (TTS_CONFIRMATION_ENTITY)
└─────────────────────┘
```

---

## 3. Module und Verantwortlichkeiten

| Modul | Verantwortung |
|-------|---------------|
| `ha_integrations/atlas_conversation/` | HA Custom Agent, leitet an /webhook/inject_text |
| `src/api/routes/ha_webhook.py` | /webhook/inject_text, /webhook/assist, /webhook/ha_action |
| `src/services/scout_direct_handler.py` | Triage, Smart Parser, HA-Calls, VPS-Fallback |
| `src/voice/smart_command_parser.py` | NL → HAAction (Pattern + LLM-Fallback) |
| `src/voice/tts_dispatcher.py` | TTS-Routing: mini, ElevenLabs, Piper |
| `src/voice/play_sound.py` | Audio-Dateien auf Mini (z.B. NASA Sound) |
| `src/connectors/home_assistant.py` | Async HA-Client (call_service, get_states) |
| `src/network/ha_client.py` | Sync HA-Client (call_service, send_whatsapp) |

---

## 4. Umgebungsvariablen

| Variable | Beschreibung | Default |
|----------|--------------|---------|
| `SCOUT_DIRECT_MODE` | Scout-Direct-Handler aktiv | false |
| `HASS_URL` / `HA_URL` | Home Assistant URL | - |
| `HASS_TOKEN` / `HA_TOKEN` | HA Long-Lived Token | - |
| `HA_WEBHOOK_TOKEN` | Bearer für /webhook/* | - |
| `TTS_TARGET` | Assist-TTS: mini, elevenlabs, elevenlabs_stream, both | mini |
| `TTS_CONFIRMATION_ENTITY` | media_player für TTS | media_player.schreibtisch |
| `ELEVENLABS_API_KEY` | ElevenLabs TTS | - |
| `CORE_HOST_IP` | IP für Stream (Mini → CORE) | 192.168.178.20 |
| `TTS_STREAM_PORT` | HTTP-Port für Audio-Stream | 8002 |

---

## 5. Entity Resolution (Smart Parser)

- **Quelle:** `context["entities"]` oder `data/home_assistant/states.json`
- **Aktualisierung:** `python -m src.scripts.fetch_ha_data` (falls vorhanden)
- **Fuzzy-Match:** rapidfuzz gegen friendly_name, entity_id
- **Patterns:** Ein/Aus, Helligkeit %, Farbe, Temperatur, Lautstärke

---

## 6. NASA Mission Complete Sound

- **Pfad:** `data/sounds/nasa_mission_complete.mp3`
- **Download:** `python -m src.scripts.download_nasa_sound`
- **Abspielen:** `play_sound_on_mini("data/sounds/nasa_mission_complete.mp3")`

---

## 7. Referenzen

- `docs/03_INFRASTRUCTURE/SCOUT_ASSIST_PIPELINE.md` – HA-Setup
- `docs/04_PROCESSES/VOICE_SMART_COMMAND_PATTERNS.md` – Parser-Patterns
- `docs/04_PROCESSES/VOICE_TROUBLESHOOTING.md` – Troubleshooting
