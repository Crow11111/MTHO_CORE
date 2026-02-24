import requests
import os
import json
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

URL = os.getenv("HASS_URL")
TOKEN = os.getenv("HASS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def list_addons():
    # Supervisor API endpoint for addons
    # URL is usually like http://IP:8123/api/hassio/...
    # But wait, the .env has HASS_URL="https://192.168.178.54:8123"
    api_url = f"{URL}/api/hassio/addons"
    print(f"Querying {api_url}...")
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        addons = data.get("data", {}).get("addons", [])
        print(f"Found {len(addons)} addons.")
        
        ollama_addons = []
        for addon in addons:
            name = addon.get("name", "")
            slug = addon.get("slug", "")
            version = addon.get("version", "")
            update_available = addon.get("update_available", False)
            
            if "ollama" in name.lower() or "ollama" in slug.lower():
                print(f"Addon: {name} (Slug: {slug}), Version: {version}, Update available: {update_available}")
                ollama_addons.append(addon)
        
        return ollama_addons
    except Exception as e:
        print(f"Error listing addons: {e}")
        return []

def update_addon(slug):
    api_url = f"{URL}/api/hassio/addons/{slug}/update"
    print(f"Updating addon {slug} via {api_url}...")
    
    try:
        response = requests.post(api_url, headers=headers, verify=False, timeout=300) # Long timeout for updates
        response.raise_for_status()
        print(f"Successfully started update for {slug}.")
        return True
    except Exception as e:
        print(f"Error updating addon: {e}")
        return False

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    ollama_list = list_addons()
    if ollama_list:
        for addon in ollama_list:
            if addon.get("update_available"):
                update_addon(addon["slug"])
            else:
                print(f"Addon {addon['name']} is already up to date.")
    else:
        print("No Ollama addon found.")
