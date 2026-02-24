import json
import os

def inspect_schreibtisch():
    input_file = os.path.join("data", "home_assistant", "states.json")
    if not os.path.exists(input_file):
        print("States file not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    print("--- Target Entity: media_player.schreibtisch ---")
    found_target = False
    for entity in states:
        if entity["entity_id"] == "media_player.schreibtisch":
            print(json.dumps(entity, indent=2))
            found_target = True
            break
    
    if not found_target:
        print("Entity media_player.schreibtisch NOT FOUND in states.json")

    print("\n--- Related Entities (containing 'schreibtisch') ---")
    for entity in states:
        e_id = entity["entity_id"].lower()
        friendly = entity.get("attributes", {}).get("friendly_name", "").lower()
        
        if "schreibtisch" in e_id or "schreibtisch" in friendly:
            if entity["entity_id"] != "media_player.schreibtisch":
                print(f"{entity['entity_id']} ({entity.get('attributes', {}).get('friendly_name')})")

if __name__ == "__main__":
    inspect_schreibtisch()
