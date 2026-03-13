# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import sys
import os

# Root-Pfad hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.voice.elevenlabs_tts import speak_text

def main():
    print("--- ElevenLabs TTS Diagnostic ---")
    
    text = "Dies ist ein Test der neuronalen Sprachausgabe."
    print(f"Generating audio for: '{text}'")
    
    path = speak_text(
        text=text,
        role_name="core_dialog",
        play=False # Nur generieren, nicht abspielen auf Server
    )
    
    if path and os.path.exists(path):
        print(f"SUCCESS: Audio generated at {path}")
        print(f"Size: {os.path.getsize(path)} bytes")
    else:
        print("FAIL: Audio generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
