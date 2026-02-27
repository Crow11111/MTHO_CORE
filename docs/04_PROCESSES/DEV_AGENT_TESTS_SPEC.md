===== ANTWORT VOM DEV-AGENT (Gemini) =====

**Umsetzung durch Cursor-Agent:** `src/scripts/run_camera_tests.py`, `src/scripts/test_wa_webhook_direct.py`, `src/scripts/test_wa_openclaw.py`. Siehe UMSETZUNGSPLANUNG.md (MX/Tapo, WhatsApp).

**Ergänzung (OC-Kanal + Frontend-Backend):** [TEST_SZENARIEN_OC_UND_FRONTEND.md](TEST_SZENARIEN_OC_UND_FRONTEND.md) – Szenarien für ATLAS↔OC (Daten bei OC, Abstimmen) und Dev-Agent-Frontend↔Backend (Verbindung, kein "Nicht verbunden"). Skripte: `test_atlas_oc_channel.py`, `fetch_oc_submissions.py`, `test_frontend_backend.py`. Dev-Agent-Kontext für OC-Kanal-Review: [dev_agent_oc_kanal_context.md](dev_agent_oc_kanal_context.md).

---

Hier ist die konkrete, umsetzbare Test-Spezifikation.

### Teil 1: MX (Brio) + Tapo – Kamera-/Erkennungstests

**1. Konkrete Test-Prozedur in Schritten**
1. **Bildquelle sicherstellen:** Entweder `go2rtc` läuft auf `localhost:1984` (Stream "pc") ODER Snapshot-Server starten: 
   `python src/scripts/camera_snapshot_server.py` (im Hintergrund laufen lassen).
2. **MX Snapshots testen:** 
   `python src/scripts/mx_save_images_only.py`
3. **Brio-Szenario testen:** 
   `python src/scripts/brio_scenario_periodic.py once`
4. **Tapo testen:** 
   `python src/scripts/tapo_garden_recognize.py`

**2. Optionales Wrapper-Skript**
**Skriptname:** `src/scripts/run_camera_tests.py`
**Zweck:** Führt alle Kamera-Tests sequenziell aus und prüft die Exit-Codes.
**Aufruf:** `python src/scripts/run_camera_tests.py`
**Code-Patch (Python):**
```python
import subprocess
import sys

scripts = [
    ["python", "src/scripts/mx_save_images_only.py"],
    ["python", "src/scripts/brio_scenario_periodic.py", "once"],
    ["python", "src/scripts/tapo_garden_recognize.py"]
]

for cmd in scripts:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"FEHLER bei {' '.join(cmd)}")
        sys.exit(1)
print("Alle Kamera-Tests erfolgreich ausgeführt.")
```

**3. Erfolgskriterien ("Test bestanden")**
- **MX:** Mindestens 1 neues `.jpg` in `data/mx_test/`.
- **Brio:** Mindestens 1 neuer JSON-Eintrag in `data/brio_scenario/protocol.jsonl` (enthält Bildpfad und Gemini-Auswertung).
- **Tapo:** Mindestens 1 neues `.jpg` in `data/tapo_garden/`.
- **Allgemein:** Alle Skripte beenden sich mit Exit-Code `0`.

---

### Teil 2: WhatsApp – Tests von allen Endpunkten

#### Block 1: Test von HA aus (End-to-End über Home Assistant)
- **Vorgehen:** Eine echte Nachricht von einem registrierten Handy an die HA-WhatsApp-Nummer senden ODER das HA-Event über die Entwicklerwerkzeuge simulieren.
- **Befehl / Aktion:** 
  In HA -> Entwicklerwerkzeuge -> Ereignisse -> Ereignis auslösen (z.B. `whatsapp_message_received` mit Payload `{"sender": "123456789", "message": "Test von HA"}`).
- **Erwartetes Ergebnis:** 
  1. ATLAS_CORE empfängt den Webhook.
  2. ATLAS_CORE verarbeitet die Nachricht und ruft `send_whatsapp` via `src/network/ha_client.py` auf.
  3. Die Antwort-Nachricht kommt auf dem physischen Test-Handy an.

#### Block 2: Test von PC/Mobil (Webhook direkt)
- **Vorgehen:** Direkter POST-Request an die laufende ATLAS_CORE Instanz, um den HA-Aufruf zu simulieren.
- **Skriptname:** `src/scripts/test_wa_webhook_direct.py`
- **Zweck:** Prüft die API-Route `POST /webhook/whatsapp` isoliert vom HA-Netzwerk.
- **Aufruf:** `python src/scripts/test_wa_webhook_direct.py`
- **Code-Patch (Python):**
```python
import requests

payload = {
    "sender": "4915112345678",
    "message": "Ping von Webhook-Test"
}
url = "http://localhost:8000/webhook/whatsapp" # Port anpassen falls abweichend

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```
- **Erwartetes Ergebnis:** 
  HTTP-Status `200 OK`. Das ATLAS_CORE Log zeigt den Eingang und die Verarbeitung der Nachricht. (Achtung: Führt ggf. zu einem echten Sendeversuch an die Nummer im Payload via HA).

#### Block 3: Test von Hostinger/OpenClaw
- **Vorgehen:** Nachricht über den OpenClaw-Client an den konfigurierten Kanal senden.
- **Skriptname:** `src/scripts/test_wa_openclaw.py`
- **Zweck:** Prüft die ausgehende Verbindung zum OpenClaw-Gateway (`src/network/openclaw_client.py`).
- **Aufruf:** `python src/scripts/test_wa_openclaw.py`
- **Code-Patch (Python):**
```python
import asyncio
from src.network.openclaw_client import OpenClawClient

async def main():
    client = OpenClawClient()
    # Parameter an die tatsächliche Signatur von send_message anpassen
    success = await client.send_message(
        channel_id="TEST_CHANNEL", # Ggf. aus .env laden
        message="Testnachricht via OpenClaw"
    )
    print(f"OpenClaw Sende-Ergebnis: {success}")

if __name__ == "__main__":
    asyncio.run(main())
```
- **Erwartetes Ergebnis:** 
  Skript gibt `OpenClaw Sende-Ergebnis: True` (oder entsprechendes Erfolgs-Objekt) aus. Exit-Code `0`. Die Nachricht ist im Ziel-WhatsApp-Kanal sichtbar.
