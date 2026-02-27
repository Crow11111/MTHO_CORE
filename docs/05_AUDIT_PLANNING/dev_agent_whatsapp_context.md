# WhatsApp: Kontext für Dev-Agent (Review + Tests umsetzen)

## Ziel

- **Review:** WhatsApp-Thematik prüfen (Flows, Endpunkte, Doku).
- **Umsetzung:** Konkrete **Tests von allen Seiten des Systems zu allen anderen** – keine Theorie, sondern ausführbare Prüfungen. Es soll getestet werden:
  1. **Vom HA-Endpunkt:** Input (z. B. Nachricht/Event) → Webhook/ATLAS → Output (Antwort) kommt bei Absender/Chat an.
  2. **Vom PC/Mobil:** User sendet Nachricht (an sich selbst oder einen Chat) → Input kommt bei HA/ATLAS an → Output (Antwort) kommt bei User an.
  3. **Vom Hostinger-Endpunkt (OpenClaw):** Input (Nachricht an OpenClaw-Kanal) → wird verarbeitet → Output (Antwort) kommt im gleichen Kanal an.

Der größte Teil läuft bereits oder war in der Vergangenheit ähnlich aufgesetzt. Es geht darum, das **testbar** zu machen und Lücken zu schließen.

---

## Aktuelle Architektur (aus DEV_AGENT_UND_SCHNITTSTELLEN.md)

### Kanal 1: ATLAS über Home Assistant (WhatsApp-Addon)

- **Pfad:** WhatsApp (eingehende Nachricht) → HA (gajosu/whatsapp-ha-addon) → Event → `rest_command.atlas_whatsapp_webhook` → ATLAS_CORE FastAPI `POST /webhook/whatsapp` → LLM/TTS/HA-Services → Antwort per `send_whatsapp(to_number=sender)` → gleicher Chat.
- **Code:** `src/api/routes/whatsapp_webhook.py`, `src/network/ha_client.py`. HA: HASS_URL, HASS_TOKEN.
- **Keine separate Bot-Nummer:** Addon nutzt den persönlichen WhatsApp-Account (WhatsApp Web). Absender = `remoteJid` im Event; Antwort geht an genau diesen Absender.

### Kanal 2: OpenClaw (Hostinger)

- **Rolle:** Selbst gehostetes Gateway (WhatsApp, Telegram, Discord, iMessage) → AI-Agents. Läuft auf Hostinger in Sandbox.
- **Konfiguration:** `openclaw.json`, `channels.whatsapp.allowFrom` (z. B. WHATSAPP_TARGET_ID aus .env).
- **Bezug zu ATLAS:** Optional; zweiter Einstieg. Entweder zwei getrennte Wege oder spätere Brücke (OpenClaw-API ↔ ATLAS).

### Latenz / Platzierung

- **WhatsApp-Basis-Handler (Steuerbefehle ohne Dreadnought):** Empfohlen auf **Scout (Pi)** – HA läuft dort, niedrige Latenz, funktioniert auch wenn PC aus ist.
- **Hostinger:** OpenClaw, ChromaDB, Backup; optional zweite HA-Instanz.

---

## Relevante Dateien / Endpunkte

| Komponente | Datei / Endpunkt | Hinweis |
|------------|------------------|--------|
| ATLAS WhatsApp-Webhook | `src/api/routes/whatsapp_webhook.py` | POST /webhook/whatsapp |
| HA-Client (Antwort senden) | `src/network/ha_client.py` | HASS_URL, HASS_TOKEN |
| OpenClaw-Client | `src/network/openclaw_client.py` | Gateway-URL, Auth, check_gateway() |
| HA rest_command | Konfiguration in HA | ruft ATLAS-URL auf (Dreadnought oder Scout) |

---

## Abstimmung Trigger & Adressierung (Plan Doc)

**Bitte Abschnitt 6 ausfüllen:** Gemeinsamer Plan für sichere WhatsApp-Adressierung (keine System-Antwort ohne Trigger, Optionen Allowlist/getrennte Nummern) steht in **docs/WHATSAPP_TRIGGER_UND_ADRESSIERUNG_PLAN.md**. Dort in **Abschnitt 6 „Abstimmung OC / Dev-Agent“** deinen Teil eintragen: Vorschläge für konkrete Tests (E2E, Trigger, Allowlist), Prüfung ob Doku mit Code konsistent ist. OC trägt in demselben Abschnitt sein erprobtes Procedere ein.

---

## Erwartete Dev-Agent-Ausgabe

1. **Kurzer Review:** Sind die Flows (HA→ATLAS→Antwort, OpenClaw) und die Doku konsistent? Fehlende oder unklare Stellen?
2. **Konkrete Test-Spezifikation (umsetzbar):**
   - **Test von HA aus:** Wie löst man einen Test-Input aus (z. B. simuliertes Event oder echte Nachricht), und wie prüft man, dass die Antwort im richtigen Chat ankommt? (Skript, HA-Automation, oder Checkliste.)
   - **Test von PC/Mobil aus:** Wie sendet man eine Nachricht (an sich selbst / einen Chat), sodass sie bei HA/ATLAS ankommt, und wie prüft man die Antwort? (Konkrete Schritte oder kleines Skript, das den Webhook direkt aufruft.)
   - **Test von Hostinger/OpenClaw aus:** Wie sendet man eine Nachricht an den OpenClaw-Kanal und prüft, dass eine Antwort zurückkommt? (API-Aufruf, curl, oder Skript.)
3. **Vorschläge für Test-Skripte oder -Prozeduren:** Wo möglich, konkrete Skriptnamen (z. B. unter `src/scripts/` oder `tests/`), Aufrufparameter und erwartetes Ergebnis. Keine reine Theorie – alles so formuliert, dass es schrittweise umgesetzt werden kann.
