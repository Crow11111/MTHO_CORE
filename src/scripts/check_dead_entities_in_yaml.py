# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

HASS_URL = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "http://192.168.178.54:8123").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_states():
    try:
        resp = requests.get(f"{HASS_URL}/api/states", headers=HEADERS, verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Fehler: {e}")
        return []

def extract_entities_from_action(action):
    entities = []
    
    # action kann dict oder liste sein
    if isinstance(action, list):
        for a in action:
            entities.extend(extract_entities_from_action(a))
    elif isinstance(action, dict):
        # target -> entity_id
        target = action.get("target", {})
        if isinstance(target, dict):
            e = target.get("entity_id")
            if isinstance(e, list):
                entities.extend(e)
            elif isinstance(e, str):
                entities.append(e)
                
        # entity_id direkt in data oder top level
        e = action.get("entity_id")
        if isinstance(e, list):
            entities.extend(e)
        elif isinstance(e, str):
            entities.append(e)
            
        # condition entities
        e = action.get("entity_id")
        if action.get("condition") == "state":
            if isinstance(e, list):
                entities.extend(e)
            elif isinstance(e, str):
                entities.append(e)
                
        # rekursion für choose, if, default, etc
        for key in ["choose", "if", "then", "else", "default", "sequence"]:
            if key in action:
                entities.extend(extract_entities_from_action(action[key]))
                
    return entities

def main():
    import urllib3
    urllib3.disable_warnings()
    
    states = fetch_states()
    
    dead_entities = set()
    all_active_entities = set()
    
    for state in states:
        e = state.get("entity_id", "")
        s = state.get("state", "").lower()
        restored = state.get("attributes", {}).get("restored", False)
        
        if s in ("unavailable", "unknown") and restored:
            dead_entities.add(e)
        else:
            all_active_entities.add(e)

    automations = [s for s in states if s["entity_id"].startswith("automation.")]
    scripts = [s for s in states if s["entity_id"].startswith("script.")]
    
    print("\n=== TEAM ANALYSE: AUTOMATISIERUNGEN & SCRIPTE MIT LEICHEN ===")
    
    # We don't have the full raw yaml config via /api/states, only attributes.
    # Automatisierungen und Scripte haben in den REST API States leider nicht immer die volle Logik.
    # Besser: Wir laden die automations.yaml und scripts.yaml ueber SMB/UNC oder parsen die lokal gecachte ha_states.json?
    # Home Assistant REST API liefert nicht den Source Code von Automations. 
    # Wir muessen ueber Samba/UNC lesen.
    
    # Da wir vorher ueber den Samba-Share S:\ zugegriffen haben (Windows Node), koennen wir dort lesen.
    try:
        import yaml
        
        def check_file(filepath):
            if not os.path.exists(filepath):
                return
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            print(f"\n--- Pruefe {filepath} ---")
            for dead in sorted(dead_entities):
                if dead in content:
                    print(f"WARNUNG: Leiche '{dead}' wird in {os.path.basename(filepath)} referenziert!")
                    
        check_file("S:\\automations.yaml")
        check_file("S:\\scripts.yaml")
        check_file("S:\\scenes.yaml")
    except Exception as e:
        print(f"Konnte YAML Files auf S:\\ nicht parsen: {e}")

if __name__ == "__main__":
    main()
