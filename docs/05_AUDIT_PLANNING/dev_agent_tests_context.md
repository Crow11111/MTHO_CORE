# Kontext: MX/Tapo- und WhatsApp-Tests (umsetzbar machen)

Der Cursor-Agent wird deine Ausgabe nutzen, um konkrete Skripte zu implementieren und Tests auszuführen. Gib daher **keine Theorie**, sondern **konkrete, schrittweise umsetzbare** Spezifikationen und wo möglich **Skriptnamen, Aufrufe und erwartete Ergebnisse**.

---

## Teil 1: MX (Brio) + Tapo – Kamera-/Erkennungstests

**Ziel:** Sicherstellen, dass (1) MX-Bilder ankommen und gespeichert werden, (2) Brio-Szenario (Bild → Auswertung → Protokoll) funktioniert, (3) Tapo (Balkon/Garten) Frame geholt und optional ausgewertet wird.

**Bestehende Skripte (Projekt `src/scripts/`):**
- `mx_save_images_only.py` – holt N Snapshots von der konfigurierten Kamera (go2rtc oder CAMERA_SNAPSHOT_URL), speichert in `data/mx_test/`. Braucht: go2rtc auf localhost:1984 mit Stream „pc“ ODER `camera_snapshot_server.py` laufend und `CAMERA_SNAPSHOT_URL=http://localhost:8555/snapshot.jpg`.
- `brio_scenario_periodic.py` – ein Zyklus: Snapshot → Gemini-Auswertung (Person, Zustand) → Protokoll in `data/brio_scenario/protocol.jsonl`. Aufruf einmalig: `python src/scripts/brio_scenario_periodic.py once`.
- `tapo_garden_recognize.py` – holt einen Frame von TAPO_FRAME_URL (HTTP, ggf. HA Ingress) oder TAPO_RTSP_URL (RTSP vom Scout), speichert in `data/tapo_garden/`, optional Gemini-Erkennung. .env: TAPO_FRAME_URL oder TAPO_RTSP_URL, optional HASS_TOKEN für Ingress.

**Randbedingungen:**
- MX: Entweder go2rtc (localhost:1984) oder camera_snapshot_server (8555) muss laufen; sonst schlagen Snapshot-Abfragen fehl.
- Tapo: Scout/go2rtc oder HA Ingress; bei 401 Ingress ggf. TAPO_RTSP_URL nutzen (RTSP zum Scout).

**Erwartung an dich:**
1. **Konkrete Test-Prozedur MX:** In welcher Reihenfolge was starten (z. B. „1. Server X starten, 2. Skript Y mit Parametern Z ausführen, 3. Prüfen: Dateien in Ordner W“). Optional: ein kleines Wrapper-Skript (z. B. `run_mx_tests.py` oder Shell/Batch), das der Cursor-Agent anlegen kann.
2. **Konkrete Test-Prozedur Tapo:** Ein Aufruf + was prüfen (Datei in data/tapo_garden, Exit-Code, ggf. Log).
3. **Checkliste/Erwartung:** Was gilt als „Test bestanden“ für MX und für Tapo (z. B. mind. 1 Bild in mx_test, 1 Eintrag in protocol.jsonl, 1 Bild in tapo_garden).

---

## Teil 2: WhatsApp – Tests von allen Endpunkten

**Ziel:** Tests von allen Seiten des Systems zu allen anderen – ausführbar, nicht nur beschrieben.

**Architektur (Kurz):**
- **Kanal 1 (ATLAS über HA):** Nachricht → HA (gajosu/whatsapp-ha-addon) → Event → rest_command → ATLAS_CORE `POST /webhook/whatsapp` → Antwort per send_whatsapp(sender). Code: `src/api/routes/whatsapp_webhook.py`, `src/network/ha_client.py`. HA: HASS_URL, HASS_TOKEN.
- **Kanal 2 (OpenClaw, Hostinger):** OpenClaw-Gateway (channels.whatsapp.allowFrom); Nachricht an Kanal → Verarbeitung → Antwort im Kanal. Client: `src/network/openclaw_client.py`, Gateway-URL + Token aus .env.

**Erwartung an dich:**
1. **Test von HA aus:** Wie löst man einen Test-Input aus (simuliertes Event / echte Nachricht), und wie prüft man, dass die Antwort im richtigen Chat ankommt? Konkret: Skriptname (z. B. unter `src/scripts/` oder `tests/`), Aufruf, oder HA-Automation/Checkliste.
2. **Test von PC/Mobil (Webhook direkt):** Wie ruft man den ATLAS-Webhook mit einem Test-Payload auf (curl oder Python), und was ist das erwartete Antwortverhalten? Konkrete Befehle oder kleines Skript `test_whatsapp_webhook.py`.
3. **Test von Hostinger/OpenClaw:** Wie sendet man eine Nachricht an den OpenClaw-Kanal (API, curl, Skript) und prüft die Antwort? Konkrete Schritte oder Skript `test_openclaw_whatsapp.py`.
4. Für jedes der drei: **Erwartetes Ergebnis** (Exit-Code, HTTP-Status, Inhalt/Datei) und **„Test bestanden“-Kriterium**.

---

## Ausgabeformat

Bitte strukturiert:
1. **MX/Tapo:** Prozedur (Schritte) + optional Wrapper-Skript-Beschreibung + Erfolgskriterien.
2. **WhatsApp:** Drei Blöcke (HA, Webhook direkt, OpenClaw) mit je: Vorgehen, konkrete Befehle/Skriptname, erwartetes Ergebnis.
3. Wo du ein neues Skript vorschlägst: **Skriptname**, **Zweck**, **Aufruf**, **erwartetes Verhalten** – so dass der Cursor-Agent es 1:1 umsetzen kann.
