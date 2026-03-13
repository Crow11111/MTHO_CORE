# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
import os

def check_trackers():
    input_file = os.path.join("data", "home_assistant", "states.json")
    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    print("--- Detailed Tracker Inspection ---")
    for entity in states:
        eid = entity["entity_id"].lower()
        if eid.startswith("device_tracker.") and "iphone" in eid:
            print(f"\n{eid}:")
            print(json.dumps(entity.get("attributes", {}), indent=2))
        elif eid.startswith("sensor.") and "iphone" in eid:
             print(f"\n{eid}:")
             print(json.dumps(entity.get("attributes", {}), indent=2))

if __name__ == "__main__":
    check_trackers()
