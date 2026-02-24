import json
import os

def find_custom_tracker():
    input_file = os.path.join("data", "home_assistant", "states.json")
    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    print("--- Searching for device trackers associated with the custom integration ---")
    for entity in states:
        eid = entity["entity_id"].lower()
        if eid.startswith("device_tracker."):
            # Let's print out all device trackers that are not obviously standard ones
            # to see if we can spot the one from the "iPhone Device Tracker" integration.
            # It might just be named device_tracker.iphone but we need to check attributes.
            if "iphone" in eid or "mth" in eid:
               print(f"\n{eid}:")
               print(json.dumps(entity.get("attributes", {}), indent=2))

if __name__ == "__main__":
    find_custom_tracker()
