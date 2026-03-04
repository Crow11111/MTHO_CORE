#!/usr/bin/env python3
"""
Kurze Audio-Bestätigung über Home Assistant (z. B. Google Minis).
Entity konfigurierbar über TTS_CONFIRMATION_ENTITY (Default: media_player.schreibtisch).
Für mehrere Minis: in HA eine Gruppe anlegen (z. B. group.minis) und als Entity angeben.
"""
import asyncio
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

DEFAULT_ENTITY = "media_player.schreibtisch"
DEFAULT_MESSAGE = "Fertig."


async def main():
    entity_id = os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip() or DEFAULT_ENTITY
    message = os.getenv("TTS_CONFIRMATION_MESSAGE", DEFAULT_MESSAGE).strip() or DEFAULT_MESSAGE

    from src.connectors.home_assistant import HomeAssistantClient
    client = HomeAssistantClient()
    service_data = {"entity_id": entity_id, "message": message}

    result = await client.call_service("tts", "google_translate_say", service_data)
    if not result:
        await client.call_service("tts", "cloud_say", service_data)


if __name__ == "__main__":
    asyncio.run(main())
