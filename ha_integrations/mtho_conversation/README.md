# CORE Conversation – Custom Integration für Home Assistant

Custom Conversation Agent, der den transkribierten Text der Assist-Pipeline an CORE `/webhook/inject_text` weiterleitet und die Antwort für TTS (Piper) zurückgibt.

## Voraussetzungen

- Home Assistant mit Assist-Pipeline (Whisper STT, Piper TTS, openWakeWord)
- CORE API erreichbar (Dreadnought, z.B. `http://192.168.178.20:8000`)
- `HA_WEBHOOK_TOKEN` in CORE `.env` gesetzt

## Installation

### Option A: Manuell (custom_components)

1. Ordner `core_conversation` nach `config/custom_components/core_conversation/` kopieren:

   ```bash
   # Von CORE Repo:
   cp -r ha_integrations/core_conversation /config/custom_components/
   ```

2. Home Assistant neu starten.

3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "CORE Conversation" suchen.

4. Konfiguration:
   - **CORE API URL:** z.B. `http://192.168.178.20:8000`
   - **Bearer Token:** `HA_WEBHOOK_TOKEN` aus `c:\CORE\.env`

### Option B: HACS (falls als Custom Repo hinzugefügt)

1. HACS → Integration hinzufügen → Custom Repository
2. URL: `https://github.com/CORE/CORE`
3. Kategorie: Integration
4. "CORE Conversation" installieren

## Assist-Pipeline konfigurieren

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen** (oder bestehenden bearbeiten)
2. **Conversation Agent:** "CORE Conversation" auswählen (nicht "Home Assistant")
3. **Speech-to-Text:** Whisper
4. **Text-to-Speech:** Piper
5. **Wake Word:** openWakeWord

## Test-Prozedur

### 1. API direkt testen (ohne HA)

```bash
curl -X POST http://192.168.178.20:8000/webhook/inject_text \
  -H "Authorization: Bearer DEIN_HA_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

Erwartung: `{"status":"ok","action":"voice_processed","reply":"..."}`

### 2. Integration in HA testen

1. **Entwicklerwerkzeuge → Dienste**
2. Service: `conversation.process`
3. Daten:
   ```yaml
   text: "Licht an"
   agent_id: "<agent_id aus Pipeline-Konfiguration oder conversation.* Entity>"
   ```
   Falls unsicher: In der Assist-Pipeline-Konfiguration den CORE-Agent auswählen; die agent_id erscheint in den Entwicklerwerkzeugen bei YAML-Ansicht.
4. Ausführen → Antwort sollte erscheinen.

### 3. Voice-Pipeline testen

1. Wake Word sagen ("hey core" / "core")
2. Befehl sprechen (z.B. "Schalte das Licht an")
3. Piper sollte die CORE-Antwort vorlesen.

## Fehlerbehebung

| Symptom | Ursache | Lösung |
|--------|---------|--------|
| "CORE API nicht erreichbar" | URL falsch oder Dreadnought offline | URL prüfen, CORE starten |
| "Token ungültig (401)" | HA_WEBHOOK_TOKEN stimmt nicht | Token in .env und HA-Integration abgleichen |
| "HA_WEBHOOK_TOKEN nicht konfiguriert (503)" | .env fehlt HA_WEBHOOK_TOKEN | In CORE .env setzen |
| Keine Antwort bei Voice | Falscher Conversation Agent | Assist-Pipeline: CORE Conversation wählen |

## Architektur

```
User spricht → openWakeWord → Whisper STT → transkribierter Text
    → CORE Conversation Agent (diese Integration)
    → POST /webhook/inject_text
    → CORE Triage (command / deep_reasoning / chat)
    → Antwort-Text
    → Piper TTS → Mini-Speaker
```

**Hinweis:** Diese Integration nutzt `/webhook/inject_text` (nur Text-Rückgabe). TTS erfolgt über HA Piper. Der Endpoint `/webhook/assist` würde CORE-seitig TTS auslösen – für die Assist-Pipeline ist `inject_text` korrekt.
