# Dev-Agent & Schnittstellenbeschreibung

## Dev-Agent (ATLAS_DEV_AGENT)

### Modell
- **ATLAS-Ausgabe erfolgt ausschließlich über Pro-Tier-Modelle.** Flash/Leichtgewichte sind für produktive ATLAS-Antworten nicht vorgesehen.
- **Standard:** Gemini 3.1 Pro (`gemini-3.1-pro-preview`) über `GEMINI_API_KEY` aus `.env`.
- **Wahl per .env:** `GEMINI_DEV_AGENT_MODEL` (z.B. `gemini-3.1-pro-preview`, `gemini-3-pro-preview`, `gemini-2.5-pro`).
- **Später (optional):** Claude 4.6 / 3.5, sobald der Anthropic-Account die Modelle freischaltet.

### Abbrechen / Timeout
- **Streamlit blockiert** während des LLM-Aufrufs; es gibt derzeit **keinen Abbrechen-Button** in der UI.
- **Abbrechen:** Browser-Tab schließen oder im Terminal, in dem Streamlit läuft, **Strg+C** drücken (ggf. mehrfach). Prozess kill beendet den Request.
- Ein technisches Request-Timeout (z.B. 120 s) kann ergänzt werden; echter „Abbrechen“-Button erfordert asynchrone Ausführung (geplante Erweiterung).

### Vernetzung mit dem Rest des Projekts
- Der Dev-Agent liefert **Text (und optional Sprache über ElevenLabs)**. Code-Vorschläge, Refactor-Pläne oder Konfigurationssnippets müssen **manuell** in die entsprechenden Dateien/Strukturen übernommen werden, bis eine spätere Integration (z.B. Patch-Anwendung, Datei-Schreibfunktion) gebaut wird.
- **Rollen & STATE** kommen aus `src/config/voice_config.py` (Osmium Circle); Schnittstelle für TTS: `src/voice/elevenlabs_tts.py`.

---

## Backup

- **Plan:** Siehe [BACKUP_PLAN.md](BACKUP_PLAN.md).
- **Umsetzung:** Skript `scripts/daily_backup.py` (noch zu implementieren); Anbindung an Cron/Task Scheduler.
- **Relevante Pfade:** Projekt-Root, `data/`, `.env`, `config/`, ggf. `media/`.

---

## Netzarchitektur: Messenger & OpenClaw

### Aktuell: ATLAS-Core-WhatsApp (Home Assistant)

- **Pfad:** WhatsApp → Home Assistant (WhatsApp-Addon) → `rest_command.atlas_whatsapp_webhook` → ATLAS_CORE FastAPI (`/webhook/whatsapp`) → LLM/TTS/HA-Services.
- **Code:** `src/api/routes/whatsapp_webhook.py`, `src/network/ha_client.py` (HASS_URL, HASS_TOKEN).
- **Zielnummer für Versand:** in HA/Addon konfiguriert; Projekt-Referenz z.B. `491788360264@s.whatsapp.net` (international: **+491788360264**, ohne +049).

### OpenClaw (Hostinger)

- **Rolle:** Selbst gehostetes **Gateway** zwischen Messenger (WhatsApp, Telegram, Discord, iMessage) und AI-Agents. Läuft auf Hostinger; Referenz: [OpenClaw Docs](https://docs.openclaw.ai/).
- **Konfiguration:** z.B. `~/.openclaw/openclaw.json`; `channels.whatsapp.allowFrom` mit erlaubten Nummern (z.B. `["+491788360264"]`).
- **Bezug zu ATLAS_CORE:** OpenClaw ist ein **zweiter, optionaler Einstieg** für Chat-to-Agent (z.B. mit Anthropic). Kein Ersatz für den ATLAS-Webhook; entweder zwei getrennte Wege (zwei Nummern/Instanzen) oder spätere Brücke (OpenClaw-API ↔ ATLAS), sobald Hostinger-Instanz stabil und API-URL/Key bekannt sind.
- **In .env:** Hostinger/OpenClaw API-URL und Key können hinterlegt werden; konkrete Anbindung (z.B. Dev-Agent oder Webhook) folgt bei Bedarf.

### Übersicht

| Einstieg            | Ziel                         | Konfiguration / Code                    |
|---------------------|------------------------------|-----------------------------------------|
| HA WhatsApp-Webhook | ATLAS (Lights, TTS, LLM)     | `whatsapp_webhook.py`, HA rest_command  |
| OpenClaw (Hostinger)| Claw-Bot / Agent (z.B. Pi)   | OpenClaw Gateway, allowFrom, Docs       |

---

## Externe Dienste (Consumer / Developer / Business)

- **Klarstellung:** ATLAS_CORE nutzt durchgängig **eigene API-Keys** (`.env`). Abrechnung erfolgt direkt beim Anbieter (Google, Anthropic, ElevenLabs); es gibt keine versteckte „Consumer-Quota“ im Projektcode.
- **Cursor/IDE:** Der Chat in Cursor verbraucht Cursor-eigene Quota; der **Dev-Agent** (Streamlit + Gemini/Claude) läuft außerhalb davon über deine Keys.
- **OpenClaw (Hostinger):** Siehe Abschnitt „Netzarchitektur: Messenger & OpenClaw“ oben; Anbindung an ATLAS optional, sobald Instanz und API-Details feststehen.

---
*Stand: Projekt-Dokumentation ATLAS_CORE. Voice/UI siehe ATLAS_VOICE_ARCHITECTURE_V1.3.md.*
