# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import json
import time
import asyncio
import logging
import requests
import websockets
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ha_ui_deploy")

HA_URL = os.getenv("HA_URL", "http://192.168.178.54:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

# Disable SSL Warnings for local network
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WS_URL = HA_URL.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"
REST_API_URL = f"{HA_URL}/api"
HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------
# UI Styleguide: "Marc's Focus UI" (custom:button-card)
# ---------------------------------------------------------
MARCS_UI_CONFIG = {
    "title": "Marc's Focus",
    "views": [
        {
            "title": "Kommandozentrale",
            "path": "main",
            "theme": "dark",
            "type": "sidebar", # Nutzt Sidebar Layout für saubere Trennung
            "cards": [
                {
                    "type": "custom:button-card",
                    "entity": "media_player.samsung_s95_tv",
                    "name": "Samsung S95",
                    "icon": "mdi:television",
                    "show_state": True,
                    "styles": {
                        "card": [
                            {"background-color": "rgba(20, 20, 25, 0.9)"},
                            {"border-radius": "16px"},
                            {"box-shadow": "0px 8px 15px rgba(0,0,0,0.6)"},
                            {"padding": "10%"}]
                    },
                    "state": [
                        {
                            "value": "on",
                            "styles": {
                                "card": [{"box-shadow": "0px 0px 15px 2px rgba(0, 150, 255, 0.5)"}],
                                "icon": [{"color": "#00aaff", "animation": "blink 2s ease infinite"}]
                            }
                        }
                    ],
                    "tap_action": {
                        "action": "call-service",
                        "service": "media_player.volume_mute",
                        "service_data": {"entity_id": "media_player.samsung_s95_tv", "is_volume_muted": True}
                    }
                }
            ]
        }
    ]
}

def mute_samsung_tv(mute: bool = True):
    action = "Muting" if mute else "Unmuting"
    logger.info(f"{action} Samsung TV...")
    url = f"{REST_API_URL}/services/media_player/volume_mute"
    payload = {"entity_id": "media_player.samsung_s95_tv", "is_volume_muted": mute}
    try:
        res = requests.post(url, headers=HEADERS, json=payload, timeout=10, verify=False)
        res.raise_for_status()
        logger.info(f"{action} command successfully dispatched.")
    except Exception as e:
        logger.error(f"Failed to {action.lower()} TV: {e}")

async def safe_deploy_dashboard(dashboard_path: str, new_config: dict):
    logger.info(f"Connecting to WebSocket for SAFE deploy on '{dashboard_path}'...")
    import ssl
    ssl_context = ssl._create_unverified_context()
    
    try:
        async with websockets.connect(WS_URL, ssl=ssl_context) as ws:
            # 1. Auth
            await ws.recv()
            await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
            auth_res = json.loads(await ws.recv())
            if auth_res.get("type") != "auth_ok":
                raise Exception(f"Auth failed: {auth_res}")
            
            # 2. BACKUP PHASE (Lovelace Config abrufen)
            await ws.send(json.dumps({"id": 1, "type": "lovelace/config", "url_path": dashboard_path}))
            current_config_res = json.loads(await ws.recv())
            
            if current_config_res.get("success"):
                backup_filename = f"backup_{dashboard_path}_{int(time.time())}.json"
                with open(backup_filename, "w", encoding="utf-8") as f:
                    json.dump(current_config_res.get("result", {}), f, indent=4)
                logger.info(f"Local backup saved: {backup_filename}")
            else:
                logger.warning(f"No existing config found for '{dashboard_path}'. Proceeding without backup.")

            # 3. WRITE PHASE
            await ws.send(json.dumps({
                "id": 2,
                "type": "lovelace/config/save",
                "url_path": dashboard_path,
                "config": new_config
            }))
            save_res = json.loads(await ws.recv())
            
            if save_res.get("success"):
                logger.info(f"Successfully deployed Marc's UI to '{dashboard_path}'.")
            else:
                logger.error(f"Failed to save dashboard: {save_res.get('error')}")

    except Exception as e:
        logger.error(f"WebSocket Error: {e}")

def main():
    if not HA_TOKEN:
        logger.error("HA_TOKEN missing in .env")
        return
    
    # 1. Action Test (Unmute TV)
    mute_samsung_tv(mute=False)
    
    # 2. UI Deployment (Strictly isolated to 'dashboard-new')
    asyncio.run(safe_deploy_dashboard("dashboard-new", MARCS_UI_CONFIG))

if __name__ == "__main__":
    main()
