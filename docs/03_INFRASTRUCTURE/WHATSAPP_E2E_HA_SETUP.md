<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# WhatsApp E2E von HA – Setup und Ablauf

Damit der komplette Weg **Nachricht → HA → CORE → Antwort im Chat** funktioniert, müssen in HA zwei Dinge stehen: **rest_command** (ruft CORE auf) und **Automation** (reagiert auf das WhatsApp-Event).

**Ablauf:** Du startest CORE **einmal** (z.B. mit `START_OMEGA_COCKPIT.bat` beim Anmelden oder Tagesstart). Ab dann triggert **die eingehende @Core-Nachricht** die Kette – nicht du vor jeder WhatsApp. Optional: Autostart (siehe [WIEDER_DA_ALLES_LAEUFT.md](../05_AUDIT_PLANNING/WIEDER_DA_ALLES_LAEUFT.md) Abschnitt 6), dann ist CORE bereit sobald der Rechner läuft.

---

## 1. rest_command in HA

CORE muss von HA aus per HTTP erreichbar sein (4D_RESONATOR (CORE) oder Scout, z. B. `http://192.168.178.20:8000`). In `configuration.yaml` (oder über die HA-Oberfläche → Einstellungen → Geräte & Dienste → REST-Befehle):

```yaml
rest_command:
  atlas_whatsapp_webhook:
    url: "http://DEINE_CORE_IP:8000/webhook/whatsapp"
    method: POST
    content_type: "application/json"
    payload: '{{ payload | tojson }}'
    timeout: 15
```

- **DEINE_CORE_IP** durch die IP des Rechners ersetzen, auf dem die CORE-CORE-API läuft (z. B. 4D_RESONATOR (CORE)), oder die des Scouts, falls CORE dort läuft.
- **timeout: 15** (Sekunden): CORE antwortet bei Chat/Reasoning sofort mit HTTP 202; 15s reichen. Ohne Angabe nutzt HA 10s – ausreichend, da keine lange Wartezeit mehr im Request.
- Der Aufruf übergibt den Schlüssel **payload**; der Wert (Addon-Event-Daten) wird als JSON an CORE gesendet.

Falls du eine Konfiguration über die UI nutzt: Der REST-Befehl soll **POST** an `http://ATLAS_IP:8000/webhook/whatsapp` senden, Body = JSON aus dem übergebenen **payload**.

---

## 2. Automation in HA

Bei jeder eingehenden WhatsApp-Nachricht (Addon feuert Event) soll der rest_command mit den Event-Daten aufgerufen werden. Beispiel (YAML oder in der Automations-UI):

```yaml
- alias: "CORE: Weiterleitung WhatsApp eingehend"
  trigger:
    - platform: event
      event_type: whatsapp_message_received
  action:
    - service: rest_command.atlas_whatsapp_webhook
      data:
        payload: "{{ trigger.event.data }}"
```

- **event_type** ggf. anpassen, falls das Addon ein anderes Event nutzt (z. B. `new_whatsapp_message` o. ä.). In den Addon-Dokumenten oder unter Entwicklerwerkzeuge → Ereignisse nachsehen.

Das Skript **wire_whatsapp_ha.py** kann diese Automation in die HA-Config eintragen (per SSH auf den Scout); danach HA-Konfiguration neu laden.

---

## 2.1 Routing: @Core und @OC (nur Adressierter reagiert)

Damit nicht auf **jede** WhatsApp-Nachricht automatisch geantwortet wird:

- **Nachricht beginnt mit @Core** → CORE/Scout verarbeiten (Antwort mit **[CORE]** bzw. **[Scout]**). Präfix wird vor der Verarbeitung abgezogen.
- **Nachricht beginnt mit @OC** → nur für OC; CORE reagiert **nicht** (ignoriert).
- **Weder @Core noch @OC am Anfang** → CORE reagiert nicht.
- **@Core am Anfang, @OC später in der Nachricht** → Teil für beide; CORE verarbeitet seinen Teil, OC den nach @OC.

Details (inkl. OC-Prozedere und Antwortformat [CORE]/[OC]): **docs/WHATSAPP_ROUTING_ATLAS_OC.md**.

---

## 3. E2E-Test ausführen

**Voraussetzungen:** HA erreichbar, rest_command und Automation wie oben eingerichtet, CORE-CORE-API läuft und ist von HA aus erreichbar.

```bash
cd C:\CORE
python -m src.scripts.run_whatsapp_e2e_ha
```

Das Skript ruft den HA-Service **rest_command.atlas_whatsapp_webhook** mit einem addon-ähnlichen Payload auf (Absender = WHATSAPP_TARGET_ID aus .env, Nachricht = "E2E-Test von HA: Ping"). Damit durchläuft die gleiche Kette wie bei einer echten Nachricht: HA → CORE → Antwort per **send_whatsapp** → HA whatsapp/send_message. Wenn alles stimmt, erscheint die CORE-Antwort im Chat zu WHATSAPP_TARGET_ID (in der Regel dein eigener Chat).

---

## 4. Echte Nachricht (manueller E2E)

1. Von einem Gerät eine WhatsApp-Nachricht in einen Chat senden, der auf dem mit dem HA-Addon verbundenen Account ankommt (z. B. an dich selbst).
2. Addon löst Event aus → Automation → rest_command → CORE.
3. CORE antwortet über HA an den Absender; die Antwort erscheint im selben Chat.

---

## 5. Präfix [CORE] und [Scout] in Nachrichten

Jede **von CORE/Scout ausgelöste** WhatsApp-Antwort beginnt mit einem Präfix, damit erkennbar ist, woher die Nachricht kommt:

- **[CORE]** – Nachricht vom **4D_RESONATOR (CORE)** (volles Modell): tiefere Reasoning-Antworten, Chat, Sprachanalyse-Ergebnis.
- **[Scout]** – Nachricht vom **kleinen Modell / direkter Steuerung**: z. B. Bestätigung von HA-Steuerbefehlen („Licht an“, „Szene XY“), „Nicht verstanden“, oder kurze Systembestätigungen („Sprachmemo empfangen …“).

Implementierung: `src/api/routes/whatsapp_webhook.py` setzt den Präfix je nach Intent (command → [Scout], deep_reasoning/chat + Audio-Ergebnis → [CORE]).

---

## 6. Abgrenzung zu OpenClaw (OC)

OC (OpenClaw) hat einen **eigenen** WhatsApp-Kanal (Gateway mit Baileys auf dem VPS). Das ist ein **zweiter** Weg, unabhängig von HA. Der **HA-E2E** betrifft nur den Pfad über deinen Account + Addon + CORE. Siehe [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md).

---

## 7. Troubleshooting (Hänger / Timeout / „dreht minutenlang“)

| Symptom | Ursache | Maßnahme |
|--------|---------|---------|
| Verbindung dreht minutenlang, bricht ab, danach wieder „warten“ | HA **rest_command** wartet auf CORE-Antwort; Default-Timeout 10s. Früher: CORE führte LLM (30s+) synchron aus → HA brach ab. | CORE antwortet bei Chat/Reasoning sofort mit **HTTP 202** und verarbeitet im Hintergrund. rest_command mit `timeout: 15` reicht. Doku oben prüfen. |
| Keine Antwort im Chat | CORE-API von HA aus nicht erreichbar (Netz/Firewall, falsche IP). | `url` in rest_command prüfen (http://ATLAS_IP:8000). Von HA-Host aus: `curl -X POST http://ATLAS_IP:8000/webhook/whatsapp -H "Content-Type: application/json" -d '{}'` → erwartet 200/202 oder JSON. |
| 4xx von CORE | Falsches Payload-Format (z. B. fehlendes `message`/`key.remoteJid`). | Automation muss `payload: "{{ trigger.event.data }}"` übergeben. Addon-Event-Struktur in HA unter Entwicklerwerkzeuge → Ereignisse prüfen. |
| WhatsApp-Nachricht geht nicht raus (CORE → HA) | HA-Service `whatsapp/send_message` nicht erreichbar oder Timeout. | HASS_URL/HASS_TOKEN in .env. CORE nutzt 15s Timeout für send_whatsapp. HA-Logs und Addon-Status prüfen. |

**E2E-Test (schnell prüfbar):**

```bash
cd C:\CORE
python -m src.scripts.run_whatsapp_e2e_ha
```

Erwartung: Exit 0, in den CORE-Logs „WhatsApp Webhook“ bzw. „text_handled“/„text_queued“, und eine Antwort im Chat (z. B. „[Scout] …“ oder „[CORE] …“).
