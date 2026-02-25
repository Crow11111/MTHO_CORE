# WhatsApp E2E von HA – Setup und Ablauf

Damit der komplette Weg **Nachricht → HA → ATLAS → Antwort im Chat** funktioniert, müssen in HA zwei Dinge stehen: **rest_command** (ruft ATLAS auf) und **Automation** (reagiert auf das WhatsApp-Event).

---

## 1. rest_command in HA

ATLAS muss von HA aus per HTTP erreichbar sein (Dreadnought oder Scout, z. B. `http://192.168.178.110:8000`). In `configuration.yaml` (oder über die HA-Oberfläche → Einstellungen → Geräte & Dienste → REST-Befehle):

```yaml
rest_command:
  atlas_whatsapp_webhook:
    url: "http://DEINE_ATLAS_IP:8000/webhook/whatsapp"
    method: POST
    content_type: "application/json"
    payload: '{{ payload | tojson }}'
```

- **DEINE_ATLAS_IP** durch die IP des Rechners ersetzen, auf dem die ATLAS-CORE-API läuft (z. B. Dreadnought), oder die des Scouts, falls ATLAS dort läuft.
- Der Aufruf übergibt den Schlüssel **payload**; der Wert (Addon-Event-Daten) wird als JSON an ATLAS gesendet.

Falls du eine Konfiguration über die UI nutzt: Der REST-Befehl soll **POST** an `http://ATLAS_IP:8000/webhook/whatsapp` senden, Body = JSON aus dem übergebenen **payload**.

---

## 2. Automation in HA

Bei jeder eingehenden WhatsApp-Nachricht (Addon feuert Event) soll der rest_command mit den Event-Daten aufgerufen werden. Beispiel (YAML oder in der Automations-UI):

```yaml
- alias: "ATLAS: Weiterleitung WhatsApp eingehend"
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

## 3. E2E-Test ausführen

**Voraussetzungen:** HA erreichbar, rest_command und Automation wie oben eingerichtet, ATLAS-CORE-API läuft und ist von HA aus erreichbar.

```bash
cd C:\ATLAS_CORE
python -m src.scripts.run_whatsapp_e2e_ha
```

Das Skript ruft den HA-Service **rest_command.atlas_whatsapp_webhook** mit einem addon-ähnlichen Payload auf (Absender = WHATSAPP_TARGET_ID aus .env, Nachricht = "E2E-Test von HA: Ping"). Damit durchläuft die gleiche Kette wie bei einer echten Nachricht: HA → ATLAS → Antwort per **send_whatsapp** → HA whatsapp/send_message. Wenn alles stimmt, erscheint die ATLAS-Antwort im Chat zu WHATSAPP_TARGET_ID (in der Regel dein eigener Chat).

---

## 4. Echte Nachricht (manueller E2E)

1. Von einem Gerät eine WhatsApp-Nachricht in einen Chat senden, der auf dem mit dem HA-Addon verbundenen Account ankommt (z. B. an dich selbst).
2. Addon löst Event aus → Automation → rest_command → ATLAS.
3. ATLAS antwortet über HA an den Absender; die Antwort erscheint im selben Chat.

---

## 5. Präfix [ATLAS] und [Scout] in Nachrichten

Jede **von ATLAS/Scout ausgelöste** WhatsApp-Antwort beginnt mit einem Präfix, damit erkennbar ist, woher die Nachricht kommt:

- **[ATLAS]** – Nachricht vom **Dreadnought** (volles Modell): tiefere Reasoning-Antworten, Chat, Sprachanalyse-Ergebnis.
- **[Scout]** – Nachricht vom **kleinen Modell / direkter Steuerung**: z. B. Bestätigung von HA-Steuerbefehlen („Licht an“, „Szene XY“), „Nicht verstanden“, oder kurze Systembestätigungen („Sprachmemo empfangen …“).

Implementierung: `src/api/routes/whatsapp_webhook.py` setzt den Präfix je nach Intent (command → [Scout], deep_reasoning/chat + Audio-Ergebnis → [ATLAS]).

---

## 6. Abgrenzung zu OpenClaw (OC)

OC (OpenClaw) hat einen **eigenen** WhatsApp-Kanal (Gateway mit Baileys auf dem VPS). Das ist ein **zweiter** Weg, unabhängig von HA. Der **HA-E2E** betrifft nur den Pfad über deinen Account + Addon + ATLAS. Siehe [WHATSAPP_OPENCLAW_VS_HA.md](WHATSAPP_OPENCLAW_VS_HA.md).
