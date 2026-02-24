import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from connectors.home_assistant import HomeAssistantClient

async def start_ollama_addon():
    load_dotenv()
    client = HomeAssistantClient()

    # The Add-on slug for Ollama
    addon_slug = "76e18fb5_ollama"
    
    service_data = {
        "addon": addon_slug
    }

    logger.info(f"Attempting to start add-on {addon_slug} via HA services...")
    
    # Call hassio.addon_start
    result = await client.call_service("hassio", "addon_start", service_data)
    
    if result is not None:
        logger.info("Service call 'hassio.addon_start' executed successfully!")
        
        # Optionally, pause and check the state to confirm
        logger.info("Waiting a few seconds to verify state...")
        await asyncio.sleep(5)
        
        # Check standard HA state for the update entity (often reflects running state attributes)
        states = await client.get_states()
        for state in states:
            if state.get("entity_id") == "update.ollama_update":
                logger.info("Current Ollama entity state:")
                logger.info(state)
                break
    else:
        logger.error("Failed to call hassio.addon_start.")

if __name__ == "__main__":
    asyncio.run(start_ollama_addon())
