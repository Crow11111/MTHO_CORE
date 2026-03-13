# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import requests
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
t = os.getenv("HASS_TOKEN", "").strip("\"'")

# Try HTTP for States
try:
    r_states = requests.get(
        "http://192.168.178.54:8123/api/states",
        headers={"Authorization": f"Bearer {t}"},
        verify=False
    )
    print("HTTP /api/states:", r_states.status_code)
except Exception as e:
    print("HTTP /api/states error:", e)

# Try HTTPS for States
try:
    r_states = requests.get(
        "https://192.168.178.54:8123/api/states",
        headers={"Authorization": f"Bearer {t}"},
        verify=False
    )
    print("HTTPS /api/states:", r_states.status_code)
except Exception as e:
    print("HTTPS /api/states error:", e)

# Try HTTPS for Addons
try:
    r_addons = requests.get(
        "https://192.168.178.54:8123/api/hassio/addons",
        headers={"Authorization": f"Bearer {t}"},
        verify=False
    )
    print("HTTPS /api/hassio/addons:", r_addons.status_code)
    print(r_addons.text[:500])
except Exception as e:
    print("HTTPS /api/hassio/addons error:", e)

