# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
with open("ha_states.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for entity in data:
    if entity["entity_id"] == "input_boolean.mth91":
        print(f"mth91: {entity['state']}")
    if entity["entity_id"] == "input_boolean.mth_away":
        print(f"mth_away: {entity['state']}")
