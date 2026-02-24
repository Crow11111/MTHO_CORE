import asyncio
import json
import os
import ssl
import sys
import websockets
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

HA_TOKEN = os.getenv("HASS_TOKEN")
HA_URL = "wss://192.168.178.54:8123/api/websocket"

async def fix_automation():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    async with websockets.connect(HA_URL, ssl=ctx) as ws:
        # Auth
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        auth = json.loads(await ws.recv())
        print(f"Auth: {auth.get('type')}")
        
        # List all automations via config API
        await ws.send(json.dumps({"id": 1, "type": "config/automation/list"}))
        resp = json.loads(await ws.recv())
        
        automations = resp.get("result", [])
        print(f"Total automations: {len(automations)}")
        
        # Find ATLAS WhatsApp automation
        target = None
        for a in automations:
            alias = a.get("alias", "")
            if "atlas" in alias.lower() and "whatsapp" in alias.lower():
                print(f"\nGefunden: {alias} (id: {a.get('id')})")
                target = a
                break
        
        if not target:
            print("ATLAS WhatsApp automation not found!")
            # Show all with whatsapp in them
            for a in automations:
                if "whatsapp" in str(a).lower():
                    print(f"  - {a.get('alias')}")
            return
        
        # Find and fix the broken payload in the action
        target_id = target.get("id")
        actions = target.get("action", [])
        
        fixed = False
        for action in actions:
            data = action.get("data", {})
            payload = data.get("payload", "")
            if "trigger.event.data" in str(payload) and "to_json" not in str(payload):
                print(f"Gefunden kaputte payload: {payload}")
                data["payload"] = "{{ trigger.event.data | to_json }}"
                fixed = True
                print(f"Gepatcht!")
        
        if fixed:
            # Save the fixed automation via WebSocket
            await ws.send(json.dumps({
                "id": 2,
                "type": "config/automation/update",
                "automation_id": target_id,
                **target
            }))
            result = json.loads(await ws.recv())
            print(f"Save result: {result.get('success')} {result.get('error', '')}")
        else:
            print("Kein kaputtes payload gefunden! Aktuelle actions:")
            for a in actions:
                print(json.dumps(a, indent=2, ensure_ascii=False)[:300])

asyncio.run(fix_automation())
