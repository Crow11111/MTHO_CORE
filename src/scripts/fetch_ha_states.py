# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

if not HA_URL or not HA_TOKEN:
    print("Error: HA_URL or HA_TOKEN not found in .env")
    exit(1)

headers = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_config(endpoint, filename):
    url = f"{HA_URL}/api/{endpoint}"
    try:
        response = requests.get(url, headers=headers, verify=False) # Skip SSL verify for local/IP access
        response.raise_for_status()
        data = response.json()
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully fetched {endpoint} to {filename}")
        return data
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def fetch_states(filename):
    url = f"{HA_URL}/api/states"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        # Filter for relevant entities (automations, scripts, input_booleans, persons)
        relevant_domains = ["automation", "script", "input_boolean", "person", "device_tracker"]
        filtered_data = [
            entity for entity in data 
            if entity["entity_id"].split(".")[0] in relevant_domains
        ]
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully fetched states to {filename}")
        return filtered_data
    except Exception as e:
        print(f"Error fetching states: {e}")
        return None

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print(f"Connecting to Home Assistant at {HA_URL}...")
    
    # Fetch configurations (source code logic)
    fetch_config("config/automation/config_entries", "ha_automations.json") # Note: /config/automation might be deprecated or behave differently, let's try states first for IDs
    
    # Getting full config via API is restricted usually. 
    # Let's try to get states (which includes attributes) to find the IDs and current state.
    # For actual logic (YAML), we might need to rely on what we can see or infer, 
    # or use the /api/config/automation/config_entries if available (often not).
    # Instead, let's get all states to identify the entities first.
    
    fetch_states("ha_states.json")
    
    # Try to get raw automation config if possible (often needs specific endpoints or WS)
    # Using a known trick: listing Registry entries via WS is better, but states give us the "friendly_name" and IDs.
