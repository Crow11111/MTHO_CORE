<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Scout Assist-Pipeline: Sprachbefehle an CORE

**Zweck:** Sprachbefehle vom Scout-Mikrofon über die HA Assist-Pipeline an CORE weiterleiten. CORE führt Triage durch (HA-Aktion oder OMEGA_ATTRACTOR), die Antwort wird per TTS auf dem Mini-Speaker ausgegeben.

---

## 1. Architektur

```
User spricht
    ↓
Scout Mikrofon (USB oder integriert)
    ↓
openWakeWord ("hey core" / "core") → Pipeline startet
    ↓
Whisper STT → transkribierter Text
    ↓
CORE API (4D_RESONATOR (CORE)) POST /webhook/assist
    ↓
Triage (SLM): command | deep_reasoning | chat
    ↓
├─ command → HA-Aktion (Licht, etc.) via HAClient
└─ deep_reasoning/chat → OMEGA_ATTRACTOR oder lokales Gemini
    ↓
Antwort-Text
    ↓
Piper TTS → Mini-Speaker (media_player.schreibtisch o.ä.)
```

**Netzwerk:**
- **Scout (HA):** 192.168.178.54 (Raspi 5)
- **4D_RESONATOR (CORE) (CORE API):** 192.168.178.20, Port 8000
- Scout muss 4D_RESONATOR (CORE) per HTTP erreichen können: `http://192.168.178.20:8000`

---

## 2. CORE-Verbindung zu HA

CORE verbindet sich **zu** HA (nicht umgekehrt):

- **Client:** `src/connectors/home_assistant.py` (HomeAssistantClient)
- **Variablen:** `HASS_URL` / `HA_URL`, `HASS_TOKEN` / `HA_TOKEN`
- **Funktionen:** `call_service()`, `get_states()`, etc.
- **Richtung:** 4D_RESONATOR (CORE) → Scout (HTTPS zu 192.168.178.54:8123)

Die **Assist-Pipeline** benötigt die **umgekehrte** Richtung: HA (Scout) → CORE (4D_RESONATOR (CORE)). Dafür nutzt HA einen `rest_command`, der an die CORE API sendet.

---

## 3. Benötigte HA-Variablen (.env auf 4D_RESONATOR (CORE))

| Variable | Beschreibung | Beispiel |
|---------|--------------|----------|
| `HASS_URL` / `HA_URL` | HA-URL (Scout) | `https://192.168.178.54:8123` |
| `HASS_TOKEN` / `HA_TOKEN` | Long-Lived Token für HA | (aus HA Profil) |
| `HA_WEBHOOK_TOKEN` | Bearer-Token für `/webhook/assist`, `/webhook/inject_text` | Zufälliger String (z.B. `openssl rand -hex 24`) |

**Wichtig:** `HA_WEBHOOK_TOKEN` muss in `.env` gesetzt sein, sonst lehnt die CORE API Anfragen ab (503).

---

## 4. HA Add-ons (Scout)

| Add-on | Zweck |
|--------|-------|
| **Assist Microphone** | **Audio-Input** – liest vom USB-Mikro (Brio/Headset), streamt an Wyoming. **Ohne dieses Add-on erreicht kein Audio die Pipeline.** |
| **Whisper** | Speech-to-Text (offenes Modell, beliebige Sprache) |
| **openWakeWord** | Wake-Word-Erkennung ("hey core", "core", "computer") |
| **Piper** | Text-to-Speech (lokal, schnell) |

Installation: Einstellungen → Add-ons → Add-on-Store. Nach Installation erscheinen die Dienste unter Wyoming-Integration.

**Hinweis:** go2rtc liefert Video+Audio für RTSP/Streaming, aber **nicht** an die Assist-Pipeline. Die Pipeline braucht das Assist Microphone Add-on für Spracheingabe.

---

## 5. Wake-Word Konfiguration

- **openWakeWord** unterstützt vordefinierte und eigene Wake-Wörter.
- Für "hey core" oder "core": In der openWakeWord-Konfiguration das passende Modell wählen oder ein Custom-Modell trainieren.
- Dokumentation: [HA Wake Words](https://www.home-assistant.io/voice_control/create_wake_word/)

---

## 6. rest_command: Text an CORE senden

In `configuration.yaml` oder als YAML-Konfiguration:

```yaml
# Geheimnisse (Einstellungen → Geheimnisse oder secrets.yaml):
#   atlas_api_url: "http://192.168.178.20:8000"
#   atlas_webhook_token: "<HA_WEBHOOK_TOKEN aus .env>"

rest_command:
  atlas_assist:
    url: "{{ atlas_api_url }}/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer {{ atlas_webhook_token }}"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

**Ohne Geheimnisse (direkt, nicht empfohlen für Produktion):**

```yaml
rest_command:
  atlas_assist:
    url: "http://192.168.178.20:8000/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer DEIN_HA_WEBHOOK_TOKEN"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

---

## 7. CORE Conversation Agent (empfohlen)

**Custom Integration** `atlas_conversation` – empfängt Text von der Assist-Pipeline, sendet an CORE `/webhook/inject_text`, gibt Antwort für TTS zurück.

### 7.0 Installation der CORE Conversation Integration

1. Ordner `ha_integrations/atlas_conversation` nach `config/custom_components/atlas_conversation/` kopieren.
2. HA neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "CORE Conversation".
4. **CORE API URL:** z.B. `http://192.168.178.20:8000`
5. **Bearer Token:** `HA_WEBHOOK_TOKEN` aus `.env`

Vollständige Anleitung: `ha_integrations/atlas_conversation/README.md`

### 7.1 Workaround: input_text + Automation (falls Integration nicht nutzbar)

Wenn der Text auf anderem Weg in `input_text.assist_command` landet (z.B. von einem externen Skript oder einer anderen Integration):

```yaml
input_text:
  assist_command:
    name: "Assist-Befehl für CORE"
    max: 500

automation:
  - alias: "Assist-Text an CORE senden"
    trigger:
      - platform: state
        entity_id:
          - input_text.assist_command
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | length > 0 }}"
    action:
      - service: rest_command.atlas_assist
        data:
          text: "{{ states('input_text.assist_command') }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.assist_command
        data:
          value: ""
```

**Hinweis:** Damit die volle Voice-Pipeline funktioniert, muss der transkribierte Text aus der Assist-Pipeline in `input_text.assist_command` geschrieben werden. Dafür ist ein **Custom Conversation Agent** nötig – die CORE Conversation Integration (Abschnitt 7.0) löst das vollständig.

**Event-basierte Alternative:** `assist_pipeline.run_stage` feuert `stt-end` (mit `stt_output.text`) und `intent-start`. Eine Automation könnte auf `stt-end` triggern und CORE aufrufen – aber die Antwort kann nicht zurück in die Pipeline injiziert werden (TTS würde fehlen). Daher: Custom Agent erforderlich.

### 7.2 CORE API Antwort und TTS

Mit **CORE Conversation Integration**: Der Agent ruft `/webhook/inject_text` auf. CORE gibt `{"status":"ok","reply":"<Antworttext>"}` zurück. **HA Piper** spricht die Antwort über den konfigurierten Media Player (TTS in der Assist-Pipeline).

Ohne Custom Agent (rest_command-Workaround): `/webhook/assist` würde CORE-seitig TTS auslösen – für die volle Voice-Pipeline ist die Integration vorzuziehen.

---

## 8. Assist-Pipeline einrichten

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** z.B. "CORE"
3. **Sprache:** Deutsch (oder gewünschte Sprache)
4. **Conversation Agent:** **CORE Conversation** (nach Installation der Custom Integration, siehe Abschnitt 7.0)
5. **Speech-to-Text:** Whisper
6. **Text-to-Speech:** Piper
7. **Wake Word:** openWakeWord (falls verfügbar)

Ohne CORE Conversation Agent arbeitet die Pipeline mit dem Standard-HA-Agent. Für CORE-Anbindung die Integration aus Abschnitt 7.0 installieren.

---

## 9. Netzwerk-Checkliste

| Von | Nach | Port | Protokoll |
|-----|------|------|-----------|
| Scout (HA) | 4D_RESONATOR (CORE) | 8000 | HTTP |
| 4D_RESONATOR (CORE) | Scout (HA) | 8123 | HTTPS |
| Scout | Wyoming (Whisper, Piper, openWakeWord) | Add-on-intern | - |

**Test von Scout aus:**
```bash
# Auf dem Scout (SSH) oder von einem Gerät im gleichen Netz:
curl -X POST http://192.168.178.20:8000/webhook/assist \
  -H "Authorization: Bearer DEIN_HA_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

---

## 10. Wyoming-Integration verifizieren

**Test-Script:** `python -m src.scripts.test_ha_voice_integration`

Prüft ob Whisper STT, Piper TTS und openWakeWord in HA verfügbar sind. Nutzt `HomeAssistantClient` aus `src/connectors/home_assistant.py`; bei SSL-Problemen (Self-Signed/IP-Zertifikat) Fallback mit `requests` + `verify=False`.

**HA REST API Calls (für Voice-Status):**

| Zweck | Endpoint | Methode |
|-------|----------|---------|
| Alle Entities (STT/TTS/Wake-Word) | `/api/states` | GET |
| Whisper STT Status | Filter `stt.*` aus `/api/states` (z.B. `stt.faster_whisper`) | - |
| Piper TTS Status | Filter `tts.*` aus `/api/states` (z.B. `tts.piper`) | - |
| openWakeWord Status | Filter `wake_word.*` aus `/api/states` (z.B. `wake_word.openwakeword`) | - |
| Assist Pipelines listen | Kein dedizierter REST-Endpoint; Pipelines über UI/WebSocket | - |

**Hinweis:** Assist Pipelines werden in HA über WebSocket/UI verwaltet. Die REST API liefert nur Entities (stt.*, tts.*, wake_word.*). Der JSON-Report wird nach `data/ha_voice_integration_report.json` geschrieben.

---

## 11. Referenzen

- `src/connectors/home_assistant.py` – CORE HA-Client
- `src/api/routes/ha_webhook.py` – `/webhook/assist`, `/webhook/inject_text`
- `src/voice/tts_dispatcher.py` – TTS an Mini-Speaker
- `docs/03_INFRASTRUCTURE/SCOUT_HA_EVENT_AN_OC_BRAIN.md` – Scout-Events an OMEGA_ATTRACTOR
- [HA Assist Pipeline](https://www.home-assistant.io/integrations/assist_pipeline/)
- [HA Lokale Voice Pipeline](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- `src/scripts/test_ha_voice_integration.py` – Wyoming-Verifizierung
