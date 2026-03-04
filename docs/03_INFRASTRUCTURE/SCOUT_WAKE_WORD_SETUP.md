# Scout Wake Word & Whisper/Wyoming Setup

**Zweck:** Whisper, Piper und openWakeWord als Wyoming-Integration in Home Assistant einrichten, Assist-Pipeline mit ATLAS verbinden und Wake Word konfigurieren.

**Voraussetzung:** Add-ons Whisper, Piper, openWakeWord sind installiert und laufen (Scout/Raspi 5).

**Verwandte Docs:**
- [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) – Verfügbare vordefinierte Modelle
- [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md) – Custom Training für „hey atlas“ und „computer“

---

## 1. Wyoming-Integration hinzufügen

### 1.1 Auto-Discovery

Nach dem Start der Add-ons erscheinen die Dienste unter **Einstellungen → Geräte & Dienste → Entdeckt**. Für jede Komponente:

1. **Wyoming (Whisper)** – Configure → Submit
2. **Wyoming (Piper)** – Configure → Submit  
3. **Wyoming (openWakeWord)** – Configure → Submit

### 1.2 Manuell (falls kein Auto-Discovery)

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche: **Wyoming Protocol**
3. Host: `192.168.178.54` (Scout) oder `homeassistant` (wenn auf HA OS)
4. Port (falls Add-on exponiert):
   - Whisper: 10300
   - Piper: 10200
   - openWakeWord: 10201 (oder Add-on-Dokumentation prüfen)

**Tipp:** In den Add-on-Einstellungen „Netzwerk exponieren“ aktivieren und Port setzen, falls Discovery fehlschlägt.

---

## 2. Assist-Pipeline erstellen

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** z.B. „ATLAS“
3. **Sprache:** Deutsch (oder gewünschte Sprache)
4. **Conversation Agent:** Home Assistant (Standard) – für ATLAS-Anbindung siehe Abschnitt 6
5. **Speech-to-Text:** Wyoming (Whisper)
6. **Text-to-Speech:** Wyoming (Piper)
7. **Wake Word:** Wyoming (openWakeWord) – siehe Abschnitt 3
8. **Erstellen** / **Aktualisieren**

---

## 3. Wake Word konfigurieren

### 3.1 Vordefinierte Wake Words (openWakeWord)

1. **Einstellungen → Sprachassistenten** → Assistent bearbeiten
2. Drei-Punkte-Menü (oben rechts) → **Streaming Wake Word hinzufügen**
3. **Streaming Wake Word Engine:** openwakeword
4. **Wake Word:** z.B. **ok nabu** (zum Testen) oder ein anderes vordefiniertes Modell

**Vordefinierte Modelle:** alexa, hey_mycroft, hey_jarvis, hey_rhasspy, timer, weather.  
**„computer“** und **„atlas“** sind nicht vordefiniert – siehe [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) und 3.2.

### 3.2 Eigenes Wake Word „hey atlas“ und „computer“

1. [Wake-Word-Training (Google Colab)](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing)
2. `target_word`: `hey atlas` (oder `atlas`) bzw. `computer`
3. **Runtime → Run all** ausführen (~30–60 Min.)
4. `.tflite`-Datei herunterladen
5. Samba: `/share/openwakeword` anlegen (falls nicht vorhanden)
6. `.tflite` in `/share/openwakeword` ablegen
7. HA neu starten oder openWakeWord-Add-on neu starten
8. Assistent bearbeiten → Wake Word: eigenes Modell wählen

**Detaillierte Anleitung:** [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md)  
**Dokumentation:** [HA Wake Words erstellen](https://www.home-assistant.io/voice_control/create_wake_word/)

### 3.3 Zwei Wake Words gleichzeitig (ab HA 2025.10)

Ab Home Assistant 2025.10 unterstützen Voice Satellites **bis zu zwei Wake Words** pro Gerät.  
→ Zwei verschiedene Assistenten/Pipelines mit unterschiedlichen Wake Words (z.B. „hey atlas“ und „computer“) können parallel aktiv sein.

### 3.4 Setup-Skripte (ATLAS)

| Skript | Zweck |
|--------|-------|
| `python src/scripts/download_openwakeword_models.py --all` | Lädt vordefinierte Modelle (hey_jarvis, alexa, etc.) herunter |
| `python src/scripts/setup_scout_wake_words.py -s data/openwakeword_models -t \\\\192.168.178.54\\share\\openwakeword` | Kopiert .tflite nach Scout |

**Ablage auf Scout:** `/share/openwakeword` (Samba: `\\192.168.178.54\share\openwakeword`)

### 3.5 openWakeWord-Parameter

- **Threshold:** 0.5 (Standard)
- **Trigger Level:** 1 (Standard)
- Bei Fehlauslösungen: Threshold erhöhen (z.B. 0.6–0.7)

---

## 4. Netzwerk-Referenz

| Komponente | IP / Host | Port |
|------------|-----------|------|
| Scout (HA) | 192.168.178.54 | 8123 (HTTPS) |
| Dreadnought (ATLAS API) | 192.168.178.110 | 8000 (HTTP) |

Scout muss Dreadnought per HTTP erreichen können: `http://192.168.178.110:8000`

---

## 5. configuration.yaml – ATLAS-Anbindung

### 5.1 Geheimnisse (empfohlen)

In **Einstellungen → Geheimnisse** oder `secrets.yaml`:

```yaml
atlas_api_url: "http://192.168.178.110:8000"
atlas_webhook_token: "778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7"
```

**Hinweis:** `atlas_webhook_token` = `HA_WEBHOOK_TOKEN` aus `c:\ATLAS_CORE\.env`.

### 5.2 rest_command.atlas_assist

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

**Ohne Geheimnisse (nur für Tests):**

```yaml
rest_command:
  atlas_assist:
    url: "http://192.168.178.110:8000/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer 778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

### 5.3 input_text (Workaround)

```yaml
input_text:
  assist_command:
    name: "Assist-Befehl für ATLAS"
    max: 500
```

### 5.4 Automation: Text an ATLAS senden

```yaml
automation:
  - alias: "Assist-Text an ATLAS senden"
    description: "Leitet Text aus input_text.assist_command an ATLAS weiter"
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

**Verwendung:** Text in `input_text.assist_command` setzen (z.B. per Dashboard-Button oder Service-Aufruf) → Automation ruft ATLAS auf.

---

## 6. Voice-Pipeline → ATLAS

### 6.1 Einschränkung

Die Standard-Assist-Pipeline leitet den transkribierten Text an den **Conversation Agent** (z.B. Home Assistant). Es gibt keine direkte Möglichkeit, diesen Text an einen externen Webhook zu schicken.

### 6.2 Mögliche Ansätze

| Ansatz | Aufwand | Beschreibung |
|--------|---------|--------------|
| **input_text + Button** | Gering | Text manuell eingeben oder per Button setzen → Automation → ATLAS |
| **assist_pipeline.run_stage Event** | Mittel | Automation auf `assist_pipeline`-Event (z.B. `stt-end`, `intent-start`) – Event-Struktur prüfen |
| **Custom Conversation Agent** | Hoch | Eigene Integration, die an ATLAS weiterleitet |

### 6.3 Experimentell: Event-basierte Automation

Falls HA ein Event mit dem transkribierten Text ausgibt:

```yaml
# Beispiel – Event-Namen und Daten je nach HA-Version prüfen
automation:
  - alias: "Assist STT-Text an ATLAS (experimentell)"
    trigger:
      - platform: event
        event_type: "assist_pipeline.run_stage"
        event_data:
          stage: "stt-end"  # oder "intent-start"
    action:
      - service: rest_command.atlas_assist
        data:
          text: "{{ trigger.event.data.text | default(trigger.event.data.intent_input) }}"
```

**Hinweis:** Event-Struktur in den Entwicklerwerkzeugen (Ereignisse) prüfen.

### 6.4 ATLAS-Verhalten bei /webhook/assist

- ATLAS führt Triage durch (Befehl vs. Chat/Deep Reasoning)
- Antwort wird per TTS auf dem Mini-Speaker ausgegeben (`tts_dispatcher`, Ziel: `media_player.schreibtisch` oder `TTS_CONFIRMATION_ENTITY`)
- Keine zusätzliche HA-Automation für TTS nötig

---

## 7. Test

### 7.1 rest_command direkt testen

**Von Scout (SSH) oder einem Gerät im gleichen Netz:**

```bash
curl -X POST http://192.168.178.110:8000/webhook/assist \
  -H "Authorization: Bearer 778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

**Erwartung:** `{"status":"ok","action":"voice_processed","reply":"..."}`

### 7.2 input_text testen

1. **Entwicklerwerkzeuge → Dienste**
2. `input_text.set_value` aufrufen:
   - `entity_id`: `input_text.assist_command`
   - `value`: `Licht an`
3. Automation sollte auslösen und ATLAS aufrufen

---

## 8. Referenzen

| Thema | Datei / URL |
|-------|-------------|
| openWakeWord Modelle | [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) |
| Custom Training | [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md) |
| Download-Skript | `src/scripts/download_openwakeword_models.py` |
| Setup-Skript | `src/scripts/setup_scout_wake_words.py` |
| ATLAS HA-Client | `src/connectors/home_assistant.py` |
| Webhook-Routen | `src/api/routes/ha_webhook.py` – `/webhook/assist`, `/webhook/inject_text` |
| Auth | `src/api/auth_webhook.py` – `verify_ha_auth` (Bearer) |
| TTS | `src/voice/tts_dispatcher.py` |
| Assist-Architektur | [docs/03_INFRASTRUCTURE/SCOUT_ASSIST_PIPELINE.md](SCOUT_ASSIST_PIPELINE.md) |
| HA Voice | [home-assistant.io/voice_control](https://www.home-assistant.io/voice_control/) |
| Wyoming | [home-assistant.io/integrations/wyoming](https://www.home-assistant.io/integrations/wyoming) |
| Wake Words | [home-assistant.io/voice_control/create_wake_word](https://www.home-assistant.io/voice_control/create_wake_word/) |

---

## 9. Codebase-Check (erledigt)

| Prüfung | Ergebnis |
|---------|----------|
| `HA_WEBHOOK_TOKEN` in `.env` | ✅ `778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7` |
| Scout IP | ✅ 192.168.178.54 |
| Dreadnought IP | ✅ 192.168.178.110 |
| `/webhook/assist` Endpoint | ✅ `ha_webhook.assist_pipeline` – Payload `{"text": "..."}` |
