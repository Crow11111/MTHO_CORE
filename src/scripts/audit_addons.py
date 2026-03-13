# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import requests
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    load_dotenv()
    
    hass_token = os.getenv("HASS_TOKEN")
    if not hass_token:
        print("Error: HASS_TOKEN not found in .env file.")
        return
        
    hass_token = hass_token.strip('"').strip("'")
    
    # Der angefragte HTTP-Endpunkt (schlägt meist durch SSL fehl, wenn HA auf HTTPS läuft)
    url_http = "http://192.168.178.54:8123/api/hassio/addons"
    # Der HTTPS-Endpunkt (wie in HASS_URL definiert)
    url_https = "https://192.168.178.54:8123/api/hassio/addons"
    
    headers = {
        "Authorization": f"Bearer {hass_token}",
        "Content-Type": "application/json"
    }

    print("--- Audit HA Add-ons ---")
    
    # 1. Test HTTP
    try:
        print(f"Versuche HTTP: GET {url_http}")
        resp_http = requests.get(url_http, headers=headers, timeout=5)
        print(f"HTTP Status: {resp_http.status_code}")
    except Exception as e:
        print(f"HTTP Error: {e}")

    # 2. Test HTTPS
    try:
        print(f"\nVersuche HTTPS: GET {url_https}")
        resp_https = requests.get(url_https, headers=headers, verify=False, timeout=5)
        print(f"HTTPS Status: {resp_https.status_code}")
        
        if resp_https.status_code == 200:
            data = resp_https.json()
            if data.get("result") == "ok":
                addons = data.get("data", {}).get("addons", [])
                
                print("\n--- Installierte Add-ons ---")
                for addon in addons:
                    if addon.get("installed"):
                        name = addon.get("name")
                        state = addon.get("state")
                        slug = addon.get("slug")
                        version = addon.get("installed")
                        print(f"- {name} [{slug}] -> Status: {state} (Version: {version})")
        else:
            print(f"HTTPS Response Error: {resp_https.text}")
            
    except Exception as e:
        print(f"HTTPS Error: {e}")

if __name__ == "__main__":
    main()
