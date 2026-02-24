import asyncio
import json
import os
import sys
import ssl
import websockets
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv("c:/ATLAS_CORE/.env")

HA_TOKEN = os.getenv("HASS_TOKEN")
HA_URL = "wss://192.168.178.54:8123/api/websocket"

async def listen():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print(f"Verbinde mit HA WebSocket...")
    async with websockets.connect(HA_URL, ssl=ctx) as ws:
        # Auth
        msg = json.loads(await ws.recv())
        print(f"HA Version: {msg.get('ha_version', '?')}")
        
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        auth_result = json.loads(await ws.recv())
        if auth_result.get("type") == "auth_ok":
            print("Authentifiziert!")
        else:
            print("Auth fehschlagen!")
            return
        
        # Subscribe to ALL events - we want to see everything!
        await ws.send(json.dumps({"id": 1, "type": "subscribe_events"}))
        sub_result = json.loads(await ws.recv())
        print(f"Subscribed: {sub_result}")
        
        print("\n=== LIVE-MONITOR: ALLE HA-Events ===")
        print("Schick jetzt eine WhatsApp - ich logge JEDEN Event-Typ!\n")
        
        watched = set()
        while True:
            raw = await ws.recv()
            event = json.loads(raw)
            
            if event.get("type") == "event":
                event_type = event.get("event", {}).get("event_type", "")
                
                # Log any new event type we haven't seen yet
                if event_type not in watched:
                    watched.add(event_type)
                    # Only print if it could be related (filter out pure state_changed spam)
                    if event_type != "state_changed":
                        print(f"[NEUER EVENT] {event_type}")
                
                # Print ALL detail if it's whatsapp-related
                if any(x in event_type.lower() for x in ["whatsapp", "message", "wa_", "chat"]):
                    print(f"\n>>> WHATSAPP EVENT: {event_type}")
                    print(json.dumps(event.get("event", {}).get("data", {}), indent=2, ensure_ascii=False)[:2000])

asyncio.run(listen())
