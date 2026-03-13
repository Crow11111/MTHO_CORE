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
        print(f"Fehler beim Abrufen der States: {e}")
        return []

def fetch_config():
    try:
        resp = requests.get(f"{HASS_URL}/api/config", headers=HEADERS, verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der Config: {e}")
        return {}

def analyze_entities(states):
    dead_entities = []
    suspicious_entities = []
    
    for state in states:
        entity_id = state.get("entity_id", "")
        s = state.get("state", "").lower()
        
        # Leichen: restored=True und state=unavailable/unknown
        attributes = state.get("attributes", {})
        restored = attributes.get("restored", False)
        
        if s in ("unavailable", "unknown"):
            if restored:
                dead_entities.append(state)
            else:
                suspicious_entities.append(state)
                
    return dead_entities, suspicious_entities

def main():
    print("=== TEAM HA RESEARCH: Starte Entitäts-Analyse ===")
    import urllib3
    urllib3.disable_warnings()
    
    states = fetch_states()
    if not states:
        print("Keine States gefunden oder API nicht erreichbar.")
        return
        
    print(f"Gefundene Entitäten gesamt: {len(states)}")
    
    dead, suspicious = analyze_entities(states)
    
    print("\n--- KATEGORIE 1: SICHERE LEICHEN (restored & unavailable/unknown) ---")
    if not dead:
        print("Keine sicheren Leichen gefunden.")
    else:
        for d in sorted(dead, key=lambda x: x["entity_id"]):
            print(f"- {d['entity_id']} (Status: {d['state']})")
            
    print("\n--- KATEGORIE 2: WACKELKANDIDATEN (unavailable/unknown, aber nicht restored) ---")
    if not suspicious:
        print("Keine Wackelkandidaten gefunden.")
    else:
        for s in sorted(suspicious, key=lambda x: x["entity_id"]):
            print(f"- {s['entity_id']} (Status: {s['state']})")

if __name__ == "__main__":
    main()
