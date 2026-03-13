# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
CORE Voice Assistant – End-to-End Test
========================================
Simuliert: "CORE Regal 80% Helligkeit"
- Verifiziert Smart Command Parser → light.turn_on
- Optional: HA-Service-Aufruf (wenn HASS_URL gesetzt)
- Optional: NASA Sound auf Mini (wenn data/sounds/nasa_mission_complete.mp3 existiert)
"""
from __future__ import annotations

import asyncio
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))

# Fixture: Entities wie in tests/test_smart_command_parser.py
MOCK_ENTITIES = [
    {"entity_id": "light.regal", "attributes": {"friendly_name": "LED Regal"}},
    {"entity_id": "light.led_regal", "attributes": {"friendly_name": "Regal"}},
    {"entity_id": "light.deckenlampe", "attributes": {"friendly_name": "Deckenlampe"}},
]


async def test_parser():
    """1. Smart Parser: 'Regal 80% Helligkeit' → light.turn_on brightness_pct=80"""
    from src.voice.smart_command_parser import parse_command

    text = "Regal 80% Helligkeit"
    action = parse_command(text, MOCK_ENTITIES)
    assert action is not None, f"Parser sollte Match für '{text}' liefern"
    assert action.domain == "light"
    assert action.service == "turn_on"
    assert action.data.get("brightness_pct") == 80
    assert "regal" in action.entity_id.lower()
    print(f"[OK] Parser: {action.domain}.{action.service} {action.entity_id} data={action.data}")
    return action


async def test_scout_direct_handler():
    """2. scout_direct_handler: process_text mit Mock-Entities"""
    from src.services.scout_direct_handler import process_text

    text = "Regal 80% Helligkeit"
    ctx = {"entities": MOCK_ENTITIES}
    result = process_text(text, ctx)
    assert "reply" in result
    assert result.get("success") or "Befehl" in result.get("reply", "")
    print(f"[OK] scout_direct_handler: routed={result.get('routed')} reply={result['reply'][:60]}...")
    return result


async def test_ha_call(action):
    """3. Optional: Echter HA-Service-Aufruf (nur wenn HASS_URL gesetzt)"""
    if not os.getenv("HASS_URL") and not os.getenv("HA_URL"):
        print("[SKIP] HASS_URL nicht gesetzt – HA-Call übersprungen")
        return

    from src.network.ha_client import HAClient

    try:
        ha = HAClient()
        service_data = action.data if action.data else {}
        if action.entity_id:
            service_data["entity_id"] = action.entity_id
        success = ha.call_service(
            action.domain,
            action.service,
            entity_id=action.entity_id,
            service_data=service_data if service_data else None,
        )
        if success:
            print(f"[OK] HA {action.domain}.{action.service} auf {action.entity_id} ausgeführt")
        else:
            print(f"[WARN] HA-Call fehlgeschlagen (Entity evtl. nicht vorhanden)")
    except Exception as e:
        print(f"[WARN] HA-Call: {e}")


async def test_nasa_sound():
    """4. NASA Sound auf Mini (wenn Datei existiert)"""
    path = os.path.join(ROOT, "data", "sounds", "nasa_mission_complete.mp3")
    if not os.path.isfile(path):
        print(f"[SKIP] NASA Sound nicht vorhanden. Download: python -m src.scripts.download_nasa_sound")
        return

    from src.voice.play_sound import play_sound_on_mini

    print("Spiele NASA Mission Complete auf Mini...")
    ok = await play_sound_on_mini(path)
    if ok:
        print("[OK] NASA Sound abgespielt")
    else:
        print("[WARN] NASA Sound Abspiel fehlgeschlagen (HASS_URL/TOKEN prüfen)")


async def main():
    print("=== CORE Voice E2E Test ===\n")

    action = await test_parser()
    await test_scout_direct_handler()
    await test_ha_call(action)
    await test_nasa_sound()

    print("\n=== E2E Test abgeschlossen ===")


if __name__ == "__main__":
    asyncio.run(main())
