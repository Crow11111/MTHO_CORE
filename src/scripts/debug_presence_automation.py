# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
HA Präsenz-Automatisierung Debugging.
Holt live Daten von Scout-HA via REST API, analysiert Präsenz-Logik.
"""
import os
import json
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

HASS_URL = os.getenv("HASS_URL") or os.getenv("HA_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
KEYWORDS = ["standby", "welcome", "präsenz", "presence", "away", "home", "handy", "phone", "mth91", "mth_away"]


async def fetch_states():
    """Holt alle States von HA (SSL verify=False für lokales Zertifikat)."""
    if not HASS_URL or not HASS_TOKEN:
        print("FEHLER: HASS_URL oder HASS_TOKEN nicht gesetzt (.env)")
        return None
    headers = {"Authorization": f"Bearer {HASS_TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        r = await client.get(f"{HASS_URL}/api/states", headers=headers)
        if r.status_code != 200:
            print(f"API Fehler: {r.status_code} {r.text[:200]}")
            return None
        return r.json()


def filter_by_keyword(entities, keywords):
    """Filtert Entities deren entity_id oder friendly_name ein Keyword enthält."""
    out = []
    for e in entities or []:
        eid = e.get("entity_id", "")
        fn = (e.get("attributes") or {}).get("friendly_name", "")
        text = f"{eid} {fn}".lower()
        if any(k.lower() in text for k in keywords):
            out.append(e)
    return out


def main():
    print("=" * 60)
    print("HA Präsenz-Automatisierung Debug")
    print("=" * 60)
    print(f"URL: {HASS_URL}")
    print()

    states = asyncio.run(fetch_states())
    if not states:
        print("Keine States geladen. Scout erreichbar? Netzwerk?")
        return

    # 1. Automations
    autos = [s for s in states if s["entity_id"].startswith("automation.")]
    presence_autos = filter_by_keyword(autos, KEYWORDS + ["core", "director", "mth"])
    print("--- AUTOMATIONS (präsenz-relevant) ---")
    for a in presence_autos:
        print(f"  {a['entity_id']}: {a.get('state','?')} | {a.get('attributes',{}).get('friendly_name','')}")
    print()

    # 2. Scripts
    scripts = [s for s in states if s["entity_id"].startswith("script.")]
    presence_scripts = filter_by_keyword(scripts, KEYWORDS)
    print("--- SCRIPTS (standby/welcome/etc.) ---")
    for s in presence_scripts:
        print(f"  {s['entity_id']}: {s.get('state','?')} | {s.get('attributes',{}).get('friendly_name','')}")
    print()

    # 3. Scenes
    scenes = [s for s in states if s["entity_id"].startswith("scene.")]
    presence_scenes = filter_by_keyword(scenes, KEYWORDS)
    print("--- SCENES (standby/etc.) ---")
    for s in presence_scenes:
        print(f"  {s['entity_id']}: {s.get('attributes',{}).get('friendly_name','')}")
    print()

    # 4. Device Tracker (alle + Marc-relevant)
    trackers = [s for s in states if s["entity_id"].startswith("device_tracker.")]
    iphone_trackers = [t for t in trackers if "iphone" in t["entity_id"].lower() or "my_iphone" in t["entity_id"].lower()]
    print("--- DEVICE TRACKER (iPhone/Marc) ---")
    for t in iphone_trackers:
        print(f"  {t['entity_id']}: state={t.get('state','?')} | last_changed={t.get('last_changed','?')[:19]}")
    print()

    # 5. Person Marc
    persons = [s for s in states if s["entity_id"].startswith("person.")]
    marc = [p for p in persons if "marc" in p["entity_id"].lower()]
    print("--- PERSON (Marc) ---")
    for p in marc:
        attrs = p.get("attributes", {})
        dt = attrs.get("device_trackers", [])
        src = attrs.get("source", "?")
        print(f"  {p['entity_id']}: state={p.get('state','?')} | source={src} | trackers={dt}")
    print()

    # 6. Input Booleans (Master-Switches)
    booleans = [s for s in states if s["entity_id"].startswith("input_boolean.")]
    mth_bools = [b for b in booleans if "mth" in b["entity_id"].lower()]
    print("--- INPUT BOOLEANS (mth91, mth_away) ---")
    for b in mth_bools:
        print(f"  {b['entity_id']}: {b.get('state','?')}")
    print()

    # 7. Bayesian Sensor (falls vorhanden)
    bayesian = [s for s in states if "mth_real_presence" in s["entity_id"] or "bayesian" in s["entity_id"].lower()]
    print("--- BAYESIAN / PRESENCE SENSOR ---")
    if bayesian:
        for b in bayesian:
            print(f"  {b['entity_id']}: {b.get('state','?')}")
    else:
        print("  (keiner gefunden - erwartet bei Direct Mode)")
    print()

    # 8. Automation-Details (Config API)
    print("--- CORE PRESENCE DIRECTOR (Details) ---")
    core_auto = [a for a in presence_autos if "core" in (a.get("attributes",{}).get("friendly_name","")).lower() or "director" in (a.get("attributes",{}).get("friendly_name","")).lower()]
    if core_auto:
        a = core_auto[0]
        print(f"  Entity: {a['entity_id']}")
        print(f"  State: {a.get('state')}")
        print(f"  Last triggered: {a.get('last_triggered', 'N/A')}")
    else:
        print("  Keine CORE Presence Director Automation gefunden!")
    print()

    # 9. Problem-Check
    print("=" * 60)
    print("PROBLEM-CHECK")
    print("=" * 60)
    issues = []

    # device_tracker.iphone_2 vs person.marc source
    person_marc = next((p for p in persons if "marc" in p["entity_id"].lower()), None)
    if person_marc:
        src = (person_marc.get("attributes") or {}).get("source", "")
        if src and "iphone_2" not in src and "my_iphone" in src:
            issues.append(f"Person Marc nutzt '{src}', fix_presence_automation.py nutzt 'device_tracker.iphone_2' - möglicher Mismatch!")

    # iphone_2 Status
    ip2 = next((t for t in trackers if t["entity_id"] == "device_tracker.iphone_2"), None)
    if ip2:
        if ip2.get("state") == "unavailable":
            issues.append("device_tracker.iphone_2 ist UNAVAILABLE - Automation triggert nicht!")
        elif ip2.get("state") not in ("home", "not_home"):
            issues.append(f"device_tracker.iphone_2 hat unerwarteten State: {ip2.get('state')}")
    else:
        issues.append("device_tracker.iphone_2 existiert NICHT - Automation kann nicht triggern!")

    # Automation disabled?
    for a in presence_autos:
        if a.get("state") == "off":
            issues.append(f"Automation {a['entity_id']} ist DEAKTIVIERT (state=off)!")

    if issues:
        for i in issues:
            print(f"  [!] {i}")
    else:
        print("  Keine offensichtlichen Konfigurationsfehler gefunden.")
    print()

    # Export für weitere Analyse
    out_path = os.path.join("data", "home_assistant", "debug_presence.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    export = {
        "automations": presence_autos,
        "scripts": presence_scripts,
        "scenes": presence_scenes,
        "device_trackers_iphone": iphone_trackers,
        "persons_marc": marc,
        "input_booleans_mth": mth_bools,
        "issues": issues,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"Export: {out_path}")


if __name__ == "__main__":
    main()
