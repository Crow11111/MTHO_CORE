import json
import os
from loguru import logger

def extract_automation_logic():
    input_file = os.path.join("data", "home_assistant", "states.json")
    output_dir = os.path.join("data", "home_assistant")
    
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        states = json.load(f)

    automations = []
    scripts = []

    for entity in states:
        entity_id = entity.get("entity_id", "")
        if entity_id.startswith("automation."):
            automations.append(entity)
        elif entity_id.startswith("script."):
            scripts.append(entity)

    # Save filtered lists
    with open(os.path.join(output_dir, "automations_derived.json"), "w", encoding="utf-8") as f:
        json.dump(automations, f, indent=2)
    logger.info(f"Extracted {len(automations)} automations from states.")

    with open(os.path.join(output_dir, "scripts_derived.json"), "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2)
    logger.info(f"Extracted {len(scripts)} scripts from states.")

if __name__ == "__main__":
    extract_automation_logic()
