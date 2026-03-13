# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test: POST an CORE /webhook/whatsapp (simuliert HA-Aufruf).
Prüft die API-Route isoliert. CORE API muss laufen (z. B. uvicorn auf API_PORT).
Payload-Format wie von HA rest_command: sender, message.conversation oder text/body.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
URL = f"http://{API_HOST}:{API_PORT}/webhook/whatsapp"


def main():
    try:
        import requests
    except ImportError:
        print("requests erforderlich: pip install requests")
        return 1

    # Payload wie vom WhatsApp-Addon / HA: sender + Nachricht
    payload = {
        "sender": os.getenv("WHATSAPP_TARGET_ID", "491788360264@s.whatsapp.net"),
        "message": {"conversation": "Ping von Webhook-Test"},
    }
    # Alternative Felder, die die Route akzeptiert:
    # payload = {"sender": "491788360264@s.whatsapp.net", "text": "Ping von Webhook-Test"}

    print(f"POST {URL}")
    print(f"Payload: sender={payload['sender']!r}, message={payload['message']!r}")
    try:
        r = requests.post(URL, json=payload, timeout=30)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text[:500] if r.text else '(leer)'}")
        return 0 if r.status_code == 200 else 1
    except requests.exceptions.ConnectionError:
        print("Verbindungsfehler – läuft die CORE API (uvicorn)?")
        return 1
    except Exception as e:
        print(f"Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
