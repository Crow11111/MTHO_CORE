# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
with open('ha_addons.json', 'r') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2)[:500])
