import os
import httpx
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

LEGACY_AUTOMATIONS = [
    "automation.mthone_leave_h91",
    "automation.mthone_in_h91",
    "automation.666_check_mth_else_off",
    "automation.auto_check_mth_in_h91",
    "automation.auto_check_mth_in_h91_2",
    "automation.mth_realy_not_in_h91"
]

async def disable_automations():
    logger.info("Deaktiviere alte Präsenz-Automationen via API...")
    url = f"{HASS_URL}/api/services/automation/turn_off"
    
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        for entity_id in LEGACY_AUTOMATIONS:
            try:
                payload = {"entity_id": entity_id}
                r = await client.post(url, headers=HEADERS, json=payload)
                if r.status_code == 200:
                    logger.success(f"Deaktiviert: {entity_id}")
                else:
                    logger.error(f"Fehler bei {entity_id}: {r.status_code} - {r.text}")
            except Exception as e:
                logger.error(f"Fehler bei API Call für {entity_id}: {e}")

if __name__ == "__main__":
    asyncio.run(disable_automations())
