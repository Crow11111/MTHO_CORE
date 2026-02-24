import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from connectors.home_assistant import HomeAssistantClient

async def play_sound():
    load_dotenv()
    client = HomeAssistantClient()

    # Target entity
    entity_id = "media_player.schreibtisch"
    
    # Message to speak
    message = "Dies ist ein Test. Hallo Schreibtisch."

    service_data = {
        "entity_id": entity_id,
        "message": message
    }

    logger.info(f"Playing TTS on {entity_id}...")
    
    # Try google_translate_say first, fallback to cloud_say if needed
    result = await client.call_service("tts", "google_translate_say", service_data)
    
    if result:
        logger.info("Command sent successfully.")
    else:
        logger.error("Failed to send command. Trying 'cloud_say'...")
        await client.call_service("tts", "cloud_say", service_data)

if __name__ == "__main__":
    asyncio.run(play_sound())
