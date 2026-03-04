import json
with open('ha_addons.json', 'r') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2)[:500])
