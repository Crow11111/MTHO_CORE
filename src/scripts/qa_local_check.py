# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
import os

print('--- HA STATES ---')
try:
    with open('ha_states.json', 'r') as f:
        # assume list of states
        data = json.load(f)
        # handle if it's not a list
        if isinstance(data, dict): states = data.get('data', []) # guess
        else: states = data
        
        for s in states:
            eid = s.get('entity_id', '')
            if 'wake_word' in eid or 'assist_pipeline' in eid:
                attrs = s.get('attributes', {})
                print(f'{eid}: {attrs}')
except Exception as e:
    print(f'Error reading ha_states.json: {e}')

print('\n--- CONFIG ENTRIES (PIPELINE ID) ---')
try:
    with open('ha_config_entries.json', 'r') as f:
        entries = json.load(f)
        s_entries = json.dumps(entries)
        if '01hzktez4kncsm0sr1qx32hy5x' in s_entries:
            print('Pipeline ID FOUND in config entries!')
        else:
            print('Pipeline ID NOT FOUND in config entries.')
except Exception as e:
    print(f'Error reading ha_config_entries.json: {e}')
