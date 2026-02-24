import os
import requests
import urllib3
import json
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

HASS_URL = os.getenv("HASS_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN")

headers = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

def verify_implementation():
    print(f"Checking SSL API at {HASS_URL} for implementation...")
    
    # Check for the Bayesian sensor
    r1 = requests.get(f"{HASS_URL}/api/states/binary_sensor.mth_real_presence_bayesian", headers=headers, verify=False, timeout=5)
    if r1.status_code == 200:
        print("\n--- Bayesian Sensor FOUND! ---")
        print(json.dumps(r1.json(), indent=2))
    else:
        print(f"\nBayesian Sensor NOT found. (Status {r1.status_code})")
        
    # Check for the automation
    # We can check the state of the automation or fetch all automations
    r2 = requests.get(f"{HASS_URL}/api/states", headers=headers, verify=False, timeout=5)
    if r2.status_code == 200:
        states = r2.json()
        automation_found = False
        for s in states:
            if s["entity_id"].startswith("automation."):
                fname = s.get("attributes", {}).get("friendly_name", "")
                if "ATLAS Presence Director" in fname or "MTH Presence Handler" in fname:
                    print("\n--- Automation FOUND! ---")
                    print(json.dumps(s, indent=2))
                    automation_found = True
                    break
        if not automation_found:
            print("\nAutomation NOT found.")
    else:
        print("Failed to fetch states.")

if __name__ == "__main__":
    verify_implementation()
