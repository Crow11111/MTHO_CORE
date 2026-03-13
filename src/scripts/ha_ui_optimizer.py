# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import json
import asyncio
import logging
import requests
import websockets
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ha_ui_optimizer")

HA_URL = os.getenv("HA_URL", "http://192.168.178.54:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

WS_URL = HA_URL.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"
REST_API_URL = f"{HA_URL}/api"

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# UI Styleguide: Marc's UI (Dark, High Contrast, Minimalist)
MARCS_UI_CONFIG = {
    "title": "Marc's Focus UI",
    "views": [
        {
            "title": "Main",
            "path": "main",
            "theme": "dark",
            "type": "sidebar",
            "badges": [],
            "cards": [
                {
                    "type": "weather-forecast",
                    "entity": "weather.home",
                    "show_current": True,
                    "show_forecast": False
                },
                {
                    "type": "entities",
                    "title": "Focus Lights",
                    "entities": [
                        "light.desk_light",
                        "light.ambient_room"
                    ]
                },
                {
                    "type": "media-control",
                    "entity": "media_player.samsung_s95"
                }
            ]
        }
    ]
}

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_connection() -> bool:
    try:
        res = requests.get(f"{REST_API_URL}/", headers=HEADERS, timeout=5, verify=False)
        res.raise_for_status()
        logger.info("REST API Connection: OK")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"REST API Connection Failed: {e}")
        return False

def mute_samsung_tv():
    logger.info("Muting Samsung TV...")
    entity_id = "media_player.samsung_s95"
    payload = {
        "entity_id": entity_id,
        "is_volume_muted": True
    }
    
    try:
        res = requests.post(
            f"{REST_API_URL}/services/media_player/volume_mute",
            headers=HEADERS,
            json=payload,
            timeout=10,
            verify=False
        )
        res.raise_for_status()
        
        # Verify state
        state_res = requests.get(f"{REST_API_URL}/states/{entity_id}", headers=HEADERS, timeout=5, verify=False)
        if state_res.status_code == 200:
            state_data = state_res.json()
            if state_data.get("attributes", {}).get("is_volume_muted"):
                logger.info(f"Success: {entity_id} is muted.")
            else:
                logger.warning(f"{entity_id} command sent, but state does not reflect mute.")
        else:
            logger.info(f"Command sent to {entity_id}.")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"Entity or Service not found for {entity_id}.")
        else:
            logger.error(f"HTTP Error muting TV: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network Error muting TV: {e}")

async def update_lovelace_dashboard(dashboard_path: str, config: dict):
    logger.info(f"Updating Lovelace Dashboard '{dashboard_path}' via WebSocket...")
    
    try:
        import ssl
        ssl_context = ssl._create_unverified_context()
        async with websockets.connect(WS_URL, ssl=ssl_context) as websocket:
            # 1. Auth Phase
            auth_req = await websocket.recv()
            logger.debug(f"Auth request: {auth_req}")
            
            await websocket.send(json.dumps({
                "type": "auth",
                "access_token": HA_TOKEN
            }))
            
            auth_res = json.loads(await websocket.recv())
            if auth_res.get("type") != "auth_ok":
                logger.error(f"WebSocket Auth failed: {auth_res}")
                return
            
            logger.info("WebSocket Auth: OK")
            
            # 2. Save Dashboard Phase
            msg_id = 1
            save_payload = {
                "id": msg_id,
                "type": "lovelace/config/save",
                "url_path": dashboard_path,
                "config": config
            }
            
            await websocket.send(json.dumps(save_payload))
            save_res = json.loads(await websocket.recv())
            
            if save_res.get("success"):
                logger.info(f"Successfully updated dashboard '{dashboard_path}'.")
            else:
                logger.error(f"Failed to update dashboard '{dashboard_path}': {save_res.get('error')}")
                
    except Exception as e:
        logger.error(f"WebSocket Error updating dashboard: {e}")

def main():
    if not HA_TOKEN:
        logger.error("HA_TOKEN is not set in .env")
        return

    if not check_connection():
        return

    mute_samsung_tv()
    
    # Run async dashboard update
    target_dashboard = "dashboard-sa"
    asyncio.run(update_lovelace_dashboard(target_dashboard, MARCS_UI_CONFIG))

if __name__ == "__main__":
    main()
