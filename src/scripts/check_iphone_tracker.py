# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
import os

with open("ha_states.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for entity in data:
    if entity["entity_id"] == "device_tracker.iphone_2":
        print(json.dumps(entity, indent=2, ensure_ascii=False))
        break
