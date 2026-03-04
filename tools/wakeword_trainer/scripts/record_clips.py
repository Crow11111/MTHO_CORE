import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
import shutil
import sys

# Konfiguration
SAMPLE_RATE = 16000
DURATION_POS = 2.0  # Sekunden für "ATLAS"
DURATION_NEG = 3.0  # Sekunden für Hintergrund/Negativ
WAKE_WORD = "ATLAS"

def get_base_dir():
    # scripts/..
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def setup_dirs():
    base = get_base_dir()
    pos_dir = os.path.join(base, "data", "positive")
    neg_dir = os.path.join(base, "data", "negative")
    
    os.makedirs(pos_dir, exist_ok=True)
    os.makedirs(neg_dir, exist_ok=True)
    
    return pos_dir, neg_dir

def record_sample(filename, duration, index, total, label):
    print(f"\n[{index}/{total}] Aufnahme startet in 0.5s... SAGE '{label}'")
    time.sleep(0.5)
    
    print("  >>> AUFNAHME <<<")
    try:
        recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
        sd.wait()
        
        # Trim silence at start/end (optional, keep simple for now)
        # Normalize
        # max_val = np.max(np.abs(recording))
        # if max_val > 0:
        #     recording = recording / max_val * 0.9
            
        sf.write(filename, recording, SAMPLE_RATE)
        print(f"  --- Gespeichert: {os.path.basename(filename)}")
        return True
    except Exception as e:
        print(f"  !!! FEHLER: {e}")
        return False

def main():
    print("=== ATLAS Wake Word Recorder ===")
    print("Dieses Tool nimmt deine Stimme auf, um das Wake Word 'ATLAS' zu trainieren.")
    print("Stelle sicher, dass dein Mikrofon aktiv ist.")
    print("")
    
    pos_dir, neg_dir = setup_dirs()
    
    # 1. POSITIVE SAMPLES (ATLAS)
    target_pos = 50
    current_pos = len([f for f in os.listdir(pos_dir) if f.endswith('.wav')])
    
    if current_pos < target_pos:
        print(f"\n--- SCHRITT 1: Positive Beispiele ({target_pos} Stück) ---")
        print(f"Sage bei jeder Aufnahme deutlich '{WAKE_WORD}'.")
        print(f"Drücke ENTER um zu starten (oder 'q' zum Abbrechen).")
        
        inp = input("> ")
        if inp.lower() == 'q': return

        for i in range(current_pos + 1, target_pos + 1):
            filename = os.path.join(pos_dir, f"atlas_{i:03d}.wav")
            success = record_sample(filename, DURATION_POS, i, target_pos, WAKE_WORD)
            if not success:
                print("Abbruch wegen Fehler.")
                break
            time.sleep(0.5)
    else:
        print(f"\n--- SCHRITT 1: Positive Beispiele ({current_pos}/{target_pos}) BEREITS ERLEDIGT ---")

    # 2. NEGATIVE SAMPLES (Hintergrund/Andere Wörter)
    target_neg = 20
    current_neg = len([f for f in os.listdir(neg_dir) if f.endswith('.wav')])
    
    if current_neg < target_neg:
        print(f"\n--- SCHRITT 2: Negative Beispiele ({target_neg} Stück) ---")
        print("WICHTIG: Sage JETZT NICHT 'ATLAS'.")
        print("Sage stattdessen normale Sätze, Zahlen, oder mache Hintergrundgeräusche.")
        print("Drücke ENTER um zu starten.")
        
        inp = input("> ")
        if inp.lower() == 'q': return

        for i in range(current_neg + 1, target_neg + 1):
            filename = os.path.join(neg_dir, f"negative_{i:03d}.wav")
            success = record_sample(filename, DURATION_NEG, i, target_neg, "IRGENDETWAS (NICHT ATLAS)")
            if not success:
                break
            time.sleep(0.5)
    else:
        print(f"\n--- SCHRITT 2: Negative Beispiele ({current_neg}/{target_neg}) BEREITS ERLEDIGT ---")

    print("\n=== AUFNAHME ABGESCHLOSSEN ===")
    print("Du kannst jetzt '3_TRAIN_AND_UPLOAD.bat' starten.")

if __name__ == "__main__":
    main()
