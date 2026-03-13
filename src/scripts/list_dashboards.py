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

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("list_dashboards")

HA_URL = os.getenv("HA_URL", "http://192.168.178.54:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")
WS_URL = HA_URL.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"

async def list_dashboards():
    import ssl
    ssl_context = ssl._create_unverified_context()
    async with websockets.connect(WS_URL, ssl=ssl_context) as ws:
        await ws.recv() # Auth required
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        await ws.recv() # Auth ok

        # List Dashboards
        await ws.send(json.dumps({"id": 1, "type": "lovelace/dashboards/list"}))
        res = json.loads(await ws.recv())
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(list_dashboards())