# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import httpx
import asyncio
import urllib3
from loguru import logger
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

HASS_URL = os.getenv("HASS_URL") or os.getenv("HA_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")

if not HASS_URL:
    HASS_URL = "https://192.168.178.54:8123"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

async def update_automation():
    # Updating the existing "Core Presence Director" automation
    # We use the same ID 'core_presence_director' to overwrite it.
    automation_id = "core_presence_director" 
    url = f"{HASS_URL}/api/config/automation/config/{automation_id}"

    # Person-basierte Logik: person.marc_ten_hoevel aggregiert alle device_trackers.
    # Liefert "home" (zone.home) oder "H91" (zone.home_2) wenn zuhause - beide abdecken.
    automation_config = {
        "alias": "System: CORE Presence Director (Person Mode)",
        "description": "Präsenzsteuerung über person.marc_ten_hoevel. Schaltet mth91/mth_away. Standby/Welcome-Scripts hängen an diesen Booleans.",
        "mode": "restart",
        "trigger": [
            # Ankommen: home (zone.home) oder H91 (zone.home_2)
            {"platform": "state", "entity_id": "person.marc_ten_hoevel", "to": "home", "id": "mth_arrives_home"},
            {"platform": "state", "entity_id": "person.marc_ten_hoevel", "to": "H91", "id": "mth_arrives"},
            # Abfahrt: von home oder H91 nach not_home (5 Min Puffer)
            {"platform": "state", "entity_id": "person.marc_ten_hoevel", "from": "home", "to": "not_home", "for": "00:05:00", "id": "mth_leaves"},
            {"platform": "state", "entity_id": "person.marc_ten_hoevel", "from": "H91", "to": "not_home", "for": "00:05:00", "id": "mth_leaves_h91"}
        ],
        "condition": [],
        "action": [
            {
                "choose": [
                    # Aktion: Ankommen (home oder H91)
                    {
                        "conditions": [{"condition": "or", "conditions": [{"condition": "trigger", "id": "mth_arrives"}, {"condition": "trigger", "id": "mth_arrives_home"}]}],
                        "sequence": [
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth_away"}},
                            {"service": "persistent_notification.create", "data": {"message": "CORE Presence: Welcome Home (Person)", "title": "Presence Log"}}
                        ]
                    },
                    # Aktion: Verlassen (von home oder H91)
                    {
                        "conditions": [{"condition": "or", "conditions": [{"condition": "trigger", "id": "mth_leaves"}, {"condition": "trigger", "id": "mth_leaves_h91"}]}],
                        "sequence": [
                            {"service": "input_boolean.turn_off", "target": {"entity_id": "input_boolean.mth91"}},
                            {"service": "input_boolean.turn_on", "target": {"entity_id": "input_boolean.mth_away"}},
                            {"service": "persistent_notification.create", "data": {"message": "CORE Presence: Goodbye (Person)", "title": "Presence Log"}}
                        ]
                    }
                ]
            }
        ]
    }

    print(f"Updating automation {automation_id} at {url}...")
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        try:
            r = await client.post(url, headers=HEADERS, json=automation_config)
            print(f"Status Code: {r.status_code}")
            if r.status_code in (200, 201):
                print("SUCCESS: Automation updated! Now uses person.marc_ten_hoevel (home/not_home).")
            else:
                print(f"FAILED: {r.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(update_automation())
