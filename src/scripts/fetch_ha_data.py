import asyncio
import os
import json
import sys
from loguru import logger
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from connectors.home_assistant import HomeAssistantClient

async def fetch_data():
    load_dotenv()
    
    output_dir = os.path.join("data", "home_assistant")
    os.makedirs(output_dir, exist_ok=True)
    
    client = HomeAssistantClient()
    
    logger.info("Connecting to Home Assistant...")
    if not await client.check_connection():
        logger.error("Could not connect to Home Assistant. Check your configuration.")
        return

    logger.info("Fetching States (Entities & Automations)...")
    states = await client.get_states()
    if states:
        with open(os.path.join(output_dir, "states.json"), "w", encoding="utf-8") as f:
            json.dump(states, f, indent=2)
        logger.info(f"Saved {len(states)} entity states.")

    logger.info("Fetching Configuration...")
    config = await client.get_config()
    if config:
        with open(os.path.join(output_dir, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info("Saved configuration.")

    logger.info("Fetching Services...")
    services = await client.get_services()
    if services:
        with open(os.path.join(output_dir, "services.json"), "w", encoding="utf-8") as f:
            json.dump(services, f, indent=2)
        logger.info(f"Saved {len(services)} domains of services.")

    logger.info("Fetching Automation Configuration...")
    automations = await client.get_automation_config()
    if automations:
        with open(os.path.join(output_dir, "automations_config.json"), "w", encoding="utf-8") as f:
            json.dump(automations, f, indent=2)
        logger.info(f"Saved detailed configuration of {len(automations)} automations.")
        
    logger.info("Fetching Script Configuration...")
    scripts = await client.get_script_config()
    if scripts:
        with open(os.path.join(output_dir, "scripts_config.json"), "w", encoding="utf-8") as f:
            json.dump(scripts, f, indent=2)
        logger.info(f"Saved detailed configuration of {len(scripts)} scripts.")
            
    logger.info("Data extraction complete.")

if __name__ == "__main__":
    asyncio.run(fetch_data())
