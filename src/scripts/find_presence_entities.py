import json
import os

def find_entities():
    input_file = os.path.join("data", "home_assistant", "states.json")
    if not os.path.exists(input_file):
        print("States file not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    print("--- Input Booleans (likely the mth in 91 / mth away buttons) ---")
    for entity in states:
        if entity["entity_id"].startswith("input_boolean."):
            friendly_name = entity.get("attributes", {}).get("friendly_name", "")
            print(f"{entity['entity_id']} ({friendly_name}) - State: {entity['state']}")

    print("\n--- Device Trackers ---")
    for entity in states:
        if entity["entity_id"].startswith("device_tracker."):
            friendly_name = entity.get("attributes", {}).get("friendly_name", "")
            print(f"{entity['entity_id']} ({friendly_name}) - State: {entity['state']}")

    print("\n--- Search for 'mth' or 'pc' in all entities ---")
    for entity in states:
        eid = entity["entity_id"].lower()
        fname = entity.get("attributes", {}).get("friendly_name", "").lower()
        if "mth" in eid or "mth" in fname or "pc" in eid or "pc" in fname:
            if not entity["entity_id"].startswith("light.") and not entity["entity_id"].startswith("switch.adaptive"):
                print(f"{entity['entity_id']} ({fname}) - State: {entity['state']}")

if __name__ == "__main__":
    find_entities()
