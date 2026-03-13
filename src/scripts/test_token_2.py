# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    with open("tmp_env.txt", "r", encoding="utf-16-le") as f: # PowerShell redirection is often UTF-16
        line = f.read().strip()
        t = line.split("=")[1].strip("\"'")
        
    r = requests.get(
        "https://192.168.178.54:8123/api/hassio/addons",
        headers={"Authorization": f"Bearer {t}"},
        verify=False
    )
    print("HTTPS /api/hassio/addons:", r.status_code)
    if r.status_code == 200:
        import json
        print(json.dumps(r.json(), indent=2)[:1000])
except Exception as e:
    print("Error:", e)
