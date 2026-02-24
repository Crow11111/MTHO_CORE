import asyncio
import os
import json
import httpx
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

HASS_URL = os.getenv("HASS_URL", "http://192.168.178.54:8123")
HASS_TOKEN = os.getenv("HASS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

async def create_automation():
    automation_config = {
        "alias": "System: MTH Presence Handler (Buttons Sync)",
        "description": "Schaltet mth91 und mth_away basierend auf dem kombinierten Präsenz-Sensor",
        "mode": "single",
        "trigger": [
            {
                "platform": "state",
                "entity_id": "binary_sensor.mth_anwesenheit_kombiniert",
                "to": "on",
                "id": "mth_arrives"
            },
            {
                "platform": "state",
                "entity_id": "binary_sensor.mth_anwesenheit_kombiniert",
                "to": "off",
                "id": "mth_leaves",
                "for": {"minutes": 2}
            }
        ],
        "condition": [],
        "action": [
            {
                "choose": [
                    {
                        "conditions": [{"condition": "trigger", "id": "mth_arrives"}],
                        "sequence": [
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth_away"}}
                        ]
                    },
                    {
                        "conditions": [{"condition": "trigger", "id": "mth_leaves"}],
                        "sequence": [
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth_away"}}
                        ]
                    }
                ]
            }
        ]
    }

    url = f"{HASS_URL}/api/config/automation/config"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post(url, headers=HEADERS, json=automation_config)
            logger.info(f"POST {url} -> {r.status_code}")
            if r.status_code in (200, 201):
                logger.info("Automation created via API successfully!")
            else:
                logger.error(f"Failed to create automation: {r.text}")
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_automation())
