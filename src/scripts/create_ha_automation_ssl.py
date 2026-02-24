import os
import httpx
import json
import asyncio
import urllib3
from loguru import logger
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

HASS_URL = os.getenv("HASS_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

async def create_automation():
    # Adding a unique ID explicitly and POSTing to the correct endpoint
    automation_id = "atlas_presence_director"
    url = f"{HASS_URL}/api/config/automation/config/{automation_id}"

    automation_config = {
        "alias": "System: ATLAS Presence Director",
        "description": "Ersetzt das alte Boolean-Sprawl durch eine saubere Bayes'sche Steuerung.",
        "mode": "queued",
        "trigger": [
            {
                "platform": "state",
                "entity_id": "binary_sensor.mth_real_presence_bayesian",
                "to": "on",
                "id": "confirmed_home"
            },
            {
                "platform": "state",
                "entity_id": "binary_sensor.mth_real_presence_bayesian",
                "to": "off",
                "for": "00:05:00",
                "id": "confirmed_away"
            }
        ],
        "condition": [],
        "action": [
            {
                "choose": [
                    {
                        "conditions": [{"condition": "trigger", "id": "confirmed_home"}],
                        "sequence": [
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth_away"}}
                        ]
                    },
                    {
                        "conditions": [{"condition": "trigger", "id": "confirmed_away"}],
                        "sequence": [
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth_away"}}
                        ]
                    }
                ]
            }
        ]
    }

    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        try:
            r = await client.post(url, headers=HEADERS, json=automation_config)
            logger.info(f"POST {url} -> {r.status_code}")
            if r.status_code in (200, 201):
                logger.info("Automation created via HTTPS API successfully!")
            else:
                logger.error(f"Failed to create automation: {r.text}")
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_automation())
