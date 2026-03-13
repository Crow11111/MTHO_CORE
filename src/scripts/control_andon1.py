# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from connectors.home_assistant import HomeAssistantClient

async def control_light():
    load_dotenv()
    client = HomeAssistantClient()

    # Entity ID found in previous step
    entity_id = "light.andon_1"
    
    # Parameters for "white light 100%"
    # "White" usually means setting rgb_color to [255, 255, 255] or kelvin/color_temp if supported.
    # We will try setting rgb_color to white and brightness to 255 (100%).
    service_data = {
        "entity_id": entity_id,
        "brightness": 255,
        "rgb_color": [255, 255, 255]
    }

    logger.info(f"Turning on {entity_id} to 100% White...")
    
    await client.call_service("light", "turn_on", service_data)

if __name__ == "__main__":
    asyncio.run(control_light())
