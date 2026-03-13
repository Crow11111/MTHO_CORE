# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
Lädt NASA Apollo Mission Audio (Public Domain) nach data/sounds/nasa_mission_complete.mp3.
Quelle: Honeysuckle Creek – Apollo 11 Highlights (60 min).
Für kurzen Clip: Erste ~15 Sekunden werden genutzt (Datei ist vollständig, Abspiel stoppt nach Bedarf).
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

SOUNDS_DIR = os.path.join(ROOT, "data", "sounds")
OUTPUT_PATH = os.path.join(SOUNDS_DIR, "nasa_mission_complete.mp3")

# Apollo 11 Highlights – Public Domain, NASA
# Kurzer Clip: Freesound CC0 "Eagle has landed" (5s) – alternativ Honeysuckle 60min
NASA_AUDIO_URL = "https://honeysucklecreek.net/audio/A11_highlights/Apollo_11_Highlights_32kbps.mp3"


def main():
    os.makedirs(SOUNDS_DIR, exist_ok=True)

    if os.path.isfile(OUTPUT_PATH):
        print(f"[OK] NASA Sound bereits vorhanden: {OUTPUT_PATH}")
        return 0

    try:
        import urllib.request

        print(f"Lade NASA Apollo 11 Audio (~16 MB)...")
        urllib.request.urlretrieve(NASA_AUDIO_URL, OUTPUT_PATH)
        if os.path.isfile(OUTPUT_PATH):
            size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
            print(f"[OK] Gespeichert: {OUTPUT_PATH} ({size_mb:.1f} MB)")
            print("Hinweis: Vollständige 60-min-Datei. Für kurzen Clip: Erste Sekunden abspielen.")
            return 0
    except Exception as e:
        print(f"[FEHLER] Download fehlgeschlagen: {e}")
        print("Manueller Download:")
        print(f"  {NASA_AUDIO_URL}")
        print(f"  Speichern nach: {OUTPUT_PATH}")
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
