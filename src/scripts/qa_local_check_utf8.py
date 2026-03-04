import json
import os

try:
    with open('ha_states.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        states = data if isinstance(data, list) else data.get('data', [])
        for s in states:
            eid = s.get('entity_id', '')
            if 'wake_word' in eid:
                st = s.get('state')
                at = s.get('attributes', {})
                print(f'{eid} ({st}): {at}')
except Exception as e:
    print(f'Error: {e}')
