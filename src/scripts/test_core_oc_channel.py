# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test des Kommunikationskanals CORE ↔ OC.

1. Prüft Erreichbarkeit des OpenClaw-Gateways (check_gateway).
2. Optional: Sendet eine Testnachricht an den Agenten (send_message_to_agent).

Aufruf:
  python -m src.scripts.test_core_oc_channel           # nur Gateway-Check
  python -m src.scripts.test_core_oc_channel --send    # Gateway + Testnachricht
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.network.openclaw_client import check_gateway, send_message_to_agent, is_configured

def main() -> int:
    if not is_configured():
        print("Nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN in .env).")
        return 1

    print("1. Gateway erreichbar?")
    ok, msg = check_gateway()
    print(f"   {msg}")
    if not ok:
        return 1

    if "--send" in sys.argv:
        print("2. Sende Testnachricht an Agent 'main' ...")
        ok2, response = send_message_to_agent(
            "Hallo OC, hier ist CORE. Dies ist eine Testnachricht über den direkten Kanal. Bitte bestätige kurz den Empfang."
        )
        print(f"   Erfolg: {ok2}")
        print(f"   Antwort: {response[:500] if response else '(leer)'}")
        if not ok2:
            return 1
    else:
        print("2. Übersprungen (ohne --send keine Nachricht gesendet).")

    print("Kanal-Test abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
