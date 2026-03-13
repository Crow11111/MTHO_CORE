# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Sendet eine einfache WhatsApp-Nachricht über Home Assistant
an WHATSAPP_TARGET_ID aus der .env, um den Outbound-Pfad zu testen.
"""
import os
from dotenv import load_dotenv

from src.network.ha_client import HAClient


def main() -> int:
    load_dotenv("c:/CORE/.env")
    target = (os.getenv("WHATSAPP_TARGET_ID") or "").strip()
    if not target:
        print("FEHLER: WHATSAPP_TARGET_ID in .env nicht gesetzt.")
        return 1

    text = "[CORE] Test-Nachricht über HAClient.send_whatsapp()"
    print(f"Sende WhatsApp an {target!r}: {text!r}")

    ha = HAClient()
    ok = ha.send_whatsapp(to_number=target, text=text)
    print("Ergebnis:", "OK" if ok else "FEHLER")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

