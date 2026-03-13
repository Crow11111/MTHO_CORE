# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import json
import os
import sys
import ssl
from pathlib import Path
from dotenv import load_dotenv

# Try importing websockets
try:
    import websockets
except ImportError:
    print("CRITICAL: 'websockets' library not found. Please install it with 'pip install websockets'")
    sys.exit(1)

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

HASS_URL = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "http://192.168.178.54:8123").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()

if not HASS_TOKEN:
    print("CRITICAL: No HASS_TOKEN found in .env")
    sys.exit(1)

# Construct WebSocket URL
if HASS_URL.startswith("https://"):
    WS_URL = HASS_URL.replace("https://", "wss://") + "/api/websocket"
    USE_SSL = True
elif HASS_URL.startswith("http://"):
    WS_URL = HASS_URL.replace("http://", "ws://") + "/api/websocket"
    USE_SSL = False
else:
    # Assume HTTP default if no protocol given
    WS_URL = f"ws://{HASS_URL}/api/websocket"
    USE_SSL = False

# Configure SSL context (permissive)
ssl_context = None
if USE_SSL:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

async def main():
    print(f"CONNECTING to {WS_URL} (SSL: {USE_SSL})...")
    
    try:
        # Connect with permissive SSL context and disable message size limit
        async with websockets.connect(WS_URL, ssl=ssl_context, max_size=None) as websocket:
            # 1. AUTHENTICATION
            auth_msg = await websocket.recv()
            auth_data = json.loads(auth_msg)
            
            if auth_data["type"] == "auth_required":
                print("AUTHENTICATING...")
                await websocket.send(json.dumps({
                    "type": "auth",
                    "access_token": HASS_TOKEN
                }))
                
                auth_response = await websocket.recv()
                auth_result = json.loads(auth_response)
                
                if auth_result["type"] != "auth_ok":
                    print(f"AUTH FAILED: {auth_result}")
                    return
                print("AUTH SUCCESSFUL.")
            else:
                print(f"UNEXPECTED AUTH STATE: {auth_data}")
                return

            msg_id = 1

            # 2. FETCH STATES
            print("FETCHING STATES...")
            msg_id += 1
            await websocket.send(json.dumps({
                "id": msg_id,
                "type": "get_states"
            }))
            
            states_resp = await websocket.recv()
            states_data = json.loads(states_resp)
            
            if not states_data.get("success"):
                print(f"FAILED TO FETCH STATES: {states_data}")
                return
                
            current_states = states_data["result"]
            print(f"  -> Found {len(current_states)} states.")

            # 3. FETCH ENTITY REGISTRY
            print("FETCHING ENTITY REGISTRY...")
            msg_id += 1
            await websocket.send(json.dumps({
                "id": msg_id,
                "type": "config/entity_registry/list"
            }))
            
            # Registry list can be large, increase read limit if needed (websockets handles frames automatically)
            registry_resp = await websocket.recv()
            registry_data = json.loads(registry_resp)
            
            if not registry_data.get("success"):
                print(f"FAILED TO FETCH REGISTRY: {registry_data}")
                return
                
            registry_entries = registry_data["result"]
            print(f"  -> Found {len(registry_entries)} registry entries.")

            # 4. IDENTIFY PHANTOMS
            # Logic: Entity must be in registry AND (state is 'unavailable' OR 'unknown') AND restored is True
            
            # Map registry for fast lookup
            registry_map = {entry["entity_id"]: entry for entry in registry_entries}
            
            phantoms = []
            
            for state in current_states:
                entity_id = state["entity_id"]
                s_val = state["state"]
                attrs = state.get("attributes", {})
                restored = attrs.get("restored", False)
                
                # Check if entity is in registry (we can only remove registered entities via registry API)
                if entity_id in registry_map:
                    # Check for phantom status: unavailable/unknown AND restored
                    if s_val in ["unavailable", "unknown"] and restored:
                        phantoms.append(entity_id)
            
            print(f"ANALYSIS COMPLETE: Found {len(phantoms)} PHANTOM ENTITIES (unavailable/unknown + restored).")
            
            if not phantoms:
                print("NO PHANTOMS FOUND. EXITING.")
                return

            # 5. EXECUTE PURGE
            print("--- STARTING PURGE SEQUENCE ---")
            deleted_count = 0
            
            for entity_id in phantoms:
                print(f"REMOVING: {entity_id}")
                msg_id += 1
                
                try:
                    await websocket.send(json.dumps({
                        "id": msg_id,
                        "type": "config/entity_registry/remove",
                        "entity_id": entity_id
                    }))
                    
                    # Read response (this is critical to avoid overwhelming the server and to confirm deletion)
                    # Note: responses may come out of order if we pipelined, but we are doing sync send-recv here
                    remove_resp = await websocket.recv()
                    remove_data = json.loads(remove_resp)
                    
                    if remove_data["id"] == msg_id and remove_data.get("success"):
                        print(f"  -> SUCCESS")
                        deleted_count += 1
                    else:
                        print(f"  -> FAILED: {remove_data.get('error')}")
                        
                except Exception as e:
                    print(f"  -> EXCEPTION: {e}")
                    
            print(f"MISSION COMPLETE. Removed {deleted_count}/{len(phantoms)} entities.")
            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
