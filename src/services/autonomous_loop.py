# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE: Autonomous Loop
Monitors data/events/ for new events, processes them via OC Brain, and executes actions.
"""
import os
import time
import json
import shutil
from loguru import logger
from src.network.openclaw_client import send_event_to_oc_brain
from src.services.action_dispatcher import ActionDispatcher
from src.voice.elevenlabs_tts import speak_text

# Pfade
ROOT = "c:/CORE"
EVENTS_DIR = os.path.join(ROOT, "data", "events")
PROCESSED_DIR = os.path.join(EVENTS_DIR, "processed")

SYSTEM_INSTRUCTION = (
    "Du bist CORE 1.0, die AGI-Schnittstelle von Marc. "
    "Du agierst autonom. Wenn ein Event eintrifft, analysiere es. "
    "Du kannst Home Assistant steuern mit dem Format: [HA: domain.service(entity_id, {\"key\": \"value\"})]. "
    "Halte deine Antworten präzise. Wenn eine Aktion nötig ist, führe sie aus. "
    "Deine Antwort wird laut vorgelesen (TTS)."
)

def process_event(event_path: str, dispatcher: ActionDispatcher):
    try:
        with open(event_path, "r", encoding="utf-8") as f:
            event = json.load(f)
            
        logger.info("Verarbeite Event: {} ({})", event.get("id"), event.get("event_type"))
        
        # An Brain senden mit System-Instruktion
        # Wir betten die Instruktion in das Event-Objekt ein oder senden sie separat
        input_text = f"INSTRUCTION: {SYSTEM_INSTRUCTION}\nEVENT: {json.dumps(event)}"
        
        success, response_text = send_event_to_oc_brain({"text": input_text})
        
        if success:
            logger.success("Brain Antwort erhalten.")
            
            # 1. Aktionen ausführen
            dispatcher.dispatch(response_text)
            
            # 2. Antwort sprechen (TTS)
            # Wir säubern den Text von [HA: ...] Kommandos für die Sprachausgabe
            clean_text = re.sub(r"\[HA:.*?\]", "", response_text).strip()
            if clean_text:
                logger.info("Sprachausgabe: {}", clean_text)
                speak_text(clean_text, play=True) # play=True für lokale Ausgabe wenn möglich
                
            # Event archivieren
            os.makedirs(PROCESSED_DIR, exist_ok=True)
            shutil.move(event_path, os.path.join(PROCESSED_DIR, os.path.basename(event_path)))
            return True
        else:
            logger.error("Brain Kommunikation fehlgeschlagen: {}", response_text)
            return False
            
    except Exception as e:
        logger.error("Fehler bei Event-Verarbeitung {}: {}", event_path, e)
        return False

def run_loop():
    logger.info("CORE 1.0 Autonomer Loop gestartet.")
    dispatcher = ActionDispatcher()
    
    while True:
        if not os.path.isdir(EVENTS_DIR):
            os.makedirs(EVENTS_DIR, exist_ok=True)
            
        # Neue .json Dateien suchen (ohne processed Ordner)
        files = [f for f in os.listdir(EVENTS_DIR) if f.endswith(".json")]
        
        for file in sorted(files):
            full_path = os.path.join(EVENTS_DIR, file)
            process_event(full_path, dispatcher)
            
        time.sleep(7)  # Primzahl-Zyklus: desynchronisiert Polling (V6 Zikaden-Prinzip)

import re # Fehlender import für re.sub

if __name__ == "__main__":
    run_loop()
