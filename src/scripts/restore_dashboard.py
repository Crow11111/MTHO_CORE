# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import json
import asyncio
import logging
import websockets
from dotenv import load_dotenv

# T.I.E. Logic: Restore Dashboard from local backup.
# Constraint: Minimal dependencies. 
# Input: backup_dashboard-new_1772242114.json -> Target: url_path="dashboard-new"

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("restore_dashboard")

HA_URL = os.getenv("HA_URL", "http://192.168.178.54:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

if not HA_TOKEN:
    logger.error("HA_TOKEN is missing in .env")
    exit(1)

WS_URL = HA_URL.replace("http://", "ws://").replace("https://", "wss://").rstrip("/") + "/api/websocket"
BACKUP_FILE = "backup_dashboard-new_1772242114.json"
TARGET_URL_PATH = "dashboard-new"

async def restore_dashboard():
    # 1. Read Backup
    if not os.path.exists(BACKUP_FILE):
        logger.error(f"Backup file not found: {BACKUP_FILE}")
        return

    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
        try:
            dashboard_config = json.load(f)
            logger.info(f"Loaded backup: {BACKUP_FILE} ({len(json.dumps(dashboard_config))} bytes)")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in backup: {e}")
            return

    # 2. Connect via WebSocket
    import ssl
    ssl_context = ssl._create_unverified_context()

    try:
        async with websockets.connect(WS_URL, ssl=ssl_context) as ws:
            # 3. Auth Flow
            auth_msg = await ws.recv() # Expecting {"type": "auth_required"}
            auth_json = json.loads(auth_msg)
            
            if auth_json.get("type") != "auth_required":
                logger.error(f"Unexpected auth message: {auth_msg}")
                return

            await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
            auth_response = await ws.recv() # Expecting {"type": "auth_ok"}
            auth_res_json = json.loads(auth_response)

            if auth_res_json.get("type") != "auth_ok":
                logger.error(f"Auth failed: {auth_response}")
                return
            
            logger.info("Authenticated successfully.")

            # 4. Save Config (lovelace/config/save)
            # Command ID must be unique per session.
            cmd_id = 1
            payload = {
                "id": cmd_id,
                "type": "lovelace/config/save",
                "url_path": TARGET_URL_PATH,
                "config": dashboard_config
            }
            
            logger.info(f"Sending restore command for url_path='{TARGET_URL_PATH}'...")
            await ws.send(json.dumps(payload))
            
            restore_response = await ws.recv()
            restore_res_json = json.loads(restore_response)

            if restore_res_json.get("success"):
                logger.info(f"SUCCESS: Dashboard '{TARGET_URL_PATH}' restored from {BACKUP_FILE}.")
            else:
                logger.error(f"FAILURE: Restore failed. Response: {restore_response}")

    except Exception as e:
        logger.error(f"WebSocket Error: {e}")

if __name__ == "__main__":
    asyncio.run(restore_dashboard())
