import json
import os

def list_lights():
    input_file = os.path.join("data", "home_assistant", "states.json")
    if not os.path.exists(input_file):
        print("States file not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    print("--- Light Entities ---")
    for entity in states:
        entity_id = entity.get("entity_id", "")
        if entity_id.startswith("light."):
            attrs = entity.get("attributes", {})
            friendly_name = attrs.get("friendly_name", "Unknown")
            print(f"{entity_id} ({friendly_name})")

if __name__ == "__main__":
    list_lights()
