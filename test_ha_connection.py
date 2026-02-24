import os
import sys
import json
import urllib.request
import re

env_file = "c:/ATLAS_CORE/.env"
creds = {}
try:
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                creds[k] = v.strip('"\'')
except Exception as e:
    print(f"Error reading .env: {e}")
    sys.exit(1)

url = f"{creds.get('HASS_URL')}/api/services"
headers = {
    "Authorization": f"Bearer {creds.get('HASS_TOKEN')}",
    "Content-Type": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        whatsapp_services = [d for d in data if d.get('domain') == 'whatsapp']
        print(f"HA Services containing whatsapp: {json.dumps(whatsapp_services, indent=2)}")
except Exception as e:
    print(f"Error querying HA: {e}")
