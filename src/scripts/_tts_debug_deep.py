# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import requests
import json
import urllib3
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")
urllib3.disable_warnings()

TOKEN = os.getenv("HASS_TOKEN", "")
if not TOKEN:
    raise SystemExit("HASS_TOKEN nicht gesetzt. Bitte in .env konfigurieren.")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE = "https://192.168.178.54:8123"

print("=" * 70)
print("TTS DEEP DEBUG - Was hat sich geändert?")
print("=" * 70)

# 1. Alle Automatisierungen mit "druck" oder "3d" oder "tts" oder "eleven"
print("\n[1] Automatisierungen mit TTS/Druck/ElevenLabs...")
r = requests.get(f"{BASE}/api/states", headers=H, verify=False, timeout=15)
states = r.json()

automations = [s for s in states if s["entity_id"].startswith("automation.")]
for a in automations:
    name = a["attributes"].get("friendly_name", "").lower()
    eid = a["entity_id"].lower()
    if any(kw in name or kw in eid for kw in ["druck", "3d", "print", "tts", "eleven", "sprach", "voice", "speak"]):
        print(f"  {a['entity_id']}")
        print(f"    Name: {a['attributes'].get('friendly_name')}")
        print(f"    State: {a['state']}")
        print(f"    Last triggered: {a['attributes'].get('last_triggered', 'N/A')}")
        print()

# 2. TTS-Plattformen
print("\n[2] TTS-Plattformen und Entities...")
tts_entities = [s for s in states if "tts" in s["entity_id"]]
for t in tts_entities:
    print(f"  {t['entity_id']}: {t['state']}")
    for k, v in t.get("attributes", {}).items():
        if k not in ["icon", "friendly_name"]:
            print(f"    {k}: {v}")

# 3. ElevenLabs Integration
print("\n[3] ElevenLabs Integration...")
elevenlabs = [s for s in states if "eleven" in s["entity_id"].lower() or "eleven" in str(s.get("attributes", {}).get("friendly_name", "")).lower()]
for e in elevenlabs:
    print(f"  {e['entity_id']}: {e['state']}")

# 4. Media Player Status
print("\n[4] Alle Media Player...")
mps = [s for s in states if s["entity_id"].startswith("media_player.")]
for mp in mps:
    attrs = mp.get("attributes", {})
    print(f"  {mp['entity_id']}: state={mp['state']}, type={attrs.get('device_class', 'N/A')}, friendly={attrs.get('friendly_name', 'N/A')}")

# 5. HA Config - URLs und Network
print("\n[5] HA Konfiguration...")
r2 = requests.get(f"{BASE}/api/config", headers=H, verify=False, timeout=10)
cfg = r2.json()
print(f"  internal_url: {cfg.get('internal_url')}")
print(f"  external_url: {cfg.get('external_url')}")
print(f"  version: {cfg.get('version')}")

# 6. SSL/HTTP Config
print("\n[6] HA HTTP-Config (aus components)...")
comps = cfg.get("components", [])
http_comps = [c for c in comps if "http" in c.lower() or "tts" in c.lower() or "cast" in c.lower() or "cloud" in c.lower()]
for c in sorted(http_comps):
    print(f"  - {c}")

# 7. Hole eine 3D-Druck Automatisierung im Detail
print("\n[7] 3D-Druck Automatisierungen Details...")
r3 = requests.get(f"{BASE}/api/config/automation/config", headers=H, verify=False, timeout=10)
print(f"  Automation config endpoint: {r3.status_code}")

# Versuche über services
print("\n[8] TTS Services verfügbar...")
r4 = requests.get(f"{BASE}/api/services", headers=H, verify=False, timeout=10)
services = r4.json()
for svc_domain in services:
    domain = svc_domain.get("domain", "")
    if domain == "tts":
        print(f"  Domain: {domain}")
        for svc_name, svc_data in svc_domain.get("services", {}).items():
            print(f"    - tts.{svc_name}: {svc_data.get('description', '')[:80]}")

# 9. Nabu Casa / Cloud Status
print("\n[9] Nabu Casa Cloud...")
cloud = [s for s in states if "cloud" in s["entity_id"]]
for c in cloud:
    print(f"  {c['entity_id']}: {c['state']}")
    for k, v in c.get("attributes", {}).items():
        print(f"    {k}: {v}")

print("\n" + "=" * 70)
