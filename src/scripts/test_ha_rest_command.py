import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

HA_URL = os.getenv("HASS_URL", "https://192.168.178.54:8123")
HA_TOKEN = os.getenv("HASS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json"
}

# Trigger the rest_command directly to see if it works
print("=== Test 1: Trigger rest_command.atlas_whatsapp_webhook direkt ===")
payload = {
    "payload": {"test_key": "test_value", "sender": "debug", "message": "atlas_test_ping"}
}
r = requests.post(
    f"{HA_URL}/api/services/rest_command/atlas_whatsapp_webhook",
    headers=HEADERS,
    json=payload,
    verify=False
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

print("\n=== Test 2: Lese HA Automation Status ===")
r2 = requests.get(
    f"{HA_URL}/api/states",
    headers=HEADERS,
    verify=False
)
all_states = r2.json()
atlas_automations = [s for s in all_states if "atlas" in s.get("entity_id", "").lower()]
for a in atlas_automations:
    print(f"ID: {a['entity_id']} | State: {a['state']} | Last triggered: {a['attributes'].get('last_triggered', 'never')}")
