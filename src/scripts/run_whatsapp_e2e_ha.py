# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
WhatsApp E2E von HA: Löst die komplette Kette aus (wie eine echte eingehende Nachricht).

Ablauf:
  1. Ruft den HA-Service rest_command.core_whatsapp_webhook mit einem addon-ähnlichen Payload auf.
  2. HA führt den rest_command aus → POST an CORE /webhook/whatsapp.
  3. CORE verarbeitet die Nachricht und antwortet per ha_client.send_whatsapp() an den Absender.

Voraussetzungen:
  - HA erreichbar (HASS_URL, HASS_TOKEN in .env).
  - rest_command.core_whatsapp_webhook in HA konfiguriert und zeigt auf CORE-API (Dreadnought/Scout).
  - CORE-API läuft und ist von HA aus erreichbar.
  - Optional: WhatsApp-Addon in HA, damit die Antwort tatsächlich in deinem Chat ankommt (gleiche Nummer wie Absender).

Payload-Format wie vom gajosu-Addon (Baileys-Stil): key.remoteJid, message.conversation.
"""
import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

HASS_URL = (os.getenv("HASS_URL") or "").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or "").strip()
# Absender für den Test (wird von CORE als Empfänger der Antwort genutzt)
WHATSAPP_TARGET_ID = (os.getenv("WHATSAPP_TARGET_ID") or "491788360264@s.whatsapp.net").strip()


def build_addon_style_payload(sender: str, text: str) -> dict:
    """Payload wie vom WhatsApp-Addon (key.remoteJid, message.conversation)."""
    return {
        "key": {"remoteJid": sender},
        "message": {"conversation": text},
        "sender": sender,
    }


def main():
    if not HASS_URL or not HASS_TOKEN:
        print("FEHLER: HASS_URL und HASS_TOKEN in .env setzen.")
        return 1

    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        print("requests erforderlich: pip install requests")
        return 1

    # Payload wie vom Addon-Event
    body_payload = build_addon_style_payload(WHATSAPP_TARGET_ID, "E2E-Test von HA: Ping")
    # HA rest_command erwartet oft einen Parameter "payload" mit dem Objekt, das an CORE geschickt wird
    service_data = {"payload": body_payload}

    url = f"{HASS_URL}/api/services/rest_command/core_whatsapp_webhook"
    headers = {
        "Authorization": f"Bearer {HASS_TOKEN}",
        "Content-Type": "application/json",
    }

    print("WhatsApp E2E von HA")
    print(f"  HA: {HASS_URL}")
    print(f"  Service: rest_command.core_whatsapp_webhook")
    print(f"  Absender (Test): {WHATSAPP_TARGET_ID}")
    print(f"  Nachricht: {body_payload['message']['conversation']!r}")
    print("  Rufe HA-Service auf …")

    try:
        r = requests.post(url, headers=headers, json=service_data, timeout=45, verify=False)
        print(f"  HA Response Status: {r.status_code}")
        if r.text:
            print(f"  HA Response: {r.text[:400]}")
        if r.status_code in (200, 201, 202):
            print("  OK – rest_command ausgeführt. Prüfe: CORE-Log und ob eine Antwort im WhatsApp-Chat ankommt (ggf. 202 = Verarbeitung im Hintergrund).")
            return 0
        print(f"  FEHLER – rest_command lieferte {r.status_code}. Prüfe: rest_command in HA (url, timeout), CORE-API von HA aus erreichbar?")
        return 1
    except requests.exceptions.Timeout:
        print("  FEHLER – Timeout (45s). HA oder CORE antwortet nicht. CORE-URL in rest_command prüfen, CORE-API läuft?")
        return 1
    except requests.exceptions.ConnectionError as e:
        print(f"  FEHLER – Verbindung zu HA: {e}. HASS_URL in .env prüfen.")
        return 1
    except Exception as e:
        print(f"  FEHLER: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
