import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
from datetime import datetime

# Konfiguration
SAMPLE_RATE = 16000
DURATION = 2.0  # Sekunden
OUTPUT_DIR = "data/wakeword_training/positive"
WAKE_WORD = "ATLAS"

def record_sample(index):
    filename = os.path.join(OUTPUT_DIR, f"{WAKE_WORD.lower()}_{index:03d}.wav")
    print(f"\n[{index}] Aufnahme startet in 0.5s... SAGE '{WAKE_WORD}'")
    time.sleep(0.5)
    
    print("  >>> AUFNAHME <<<")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    print("  --- Fertig ---")
    
    # Normalisieren (optional, aber gut)
    # recording = recording / np.max(np.abs(recording))
    
    sf.write(filename, recording, SAMPLE_RATE)
    print(f"Gespeichert: {filename}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"=== ATLAS Wake Word Recorder ===")
    print(f"Ziel: {OUTPUT_DIR}")
    print(f"Drücke ENTER für jede Aufnahme. 'q' zum Beenden.")
    
    count = 1
    # Zähle existierende Dateien
    existing = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.wav')]
    if existing:
        count = len(existing) + 1
        
    while True:
        inp = input(f"\nDrücke ENTER für Sample #{count} (oder 'q'): ")
        if inp.lower() == 'q':
            break
            
        try:
            record_sample(count)
            count += 1
        except Exception as e:
            print(f"Fehler: {e}")
            print("Hast du 'sounddevice' installiert? pip install sounddevice soundfile numpy")
            break

if __name__ == "__main__":
    main()
