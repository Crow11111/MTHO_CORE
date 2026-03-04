#!/usr/bin/env python3
"""
ATLAS – openWakeWord Modelle herunterladen

Lädt vordefinierte openWakeWord .tflite Modelle von GitHub Releases herunter.
Nützlich für: hey_jarvis (computer-ähnlich), hey_mycroft, alexa, etc.

Verwendung:
  python src/scripts/download_openwakeword_models.py [--output DIR] [--models alexa,hey_jarvis]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import urllib.request

RELEASE_BASE = "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1"
MODELS = {
    "alexa": "alexa_v0.1.tflite",
    "hey_mycroft": "hey_mycroft_v0.1.tflite",
    "hey_jarvis": "hey_jarvis_v0.1.tflite",
    "hey_rhasspy": "hey_rhasspy_v0.1.tflite",
    "timer": "timer_v0.1.tflite",
    "weather": "weather_v0.1.tflite",
}


def download_model(model_id: str, output_dir: Path) -> bool:
    if model_id not in MODELS:
        print(f"Unbekanntes Modell: {model_id}. Verfügbar: {', '.join(MODELS)}")
        return False
    filename = MODELS[model_id]
    url = f"{RELEASE_BASE}/{filename}"
    out_path = output_dir / filename
    try:
        print(f"Lade {model_id} -> {out_path} ...")
        urllib.request.urlretrieve(url, out_path)
        print(f"  OK: {out_path}")
        return True
    except Exception as e:
        print(f"  Fehler: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="openWakeWord Modelle herunterladen")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/openwakeword_models"),
        help="Ausgabeverzeichnis (default: data/openwakeword_models)",
    )
    parser.add_argument(
        "--models",
        "-m",
        type=str,
        default="hey_jarvis,hey_mycroft,alexa",
        help="Komma-getrennte Modell-IDs (default: hey_jarvis,hey_mycroft,alexa)",
    )
    parser.add_argument("--all", action="store_true", help="Alle Modelle herunterladen")
    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        model_ids = list(MODELS.keys())
    else:
        model_ids = [m.strip() for m in args.models.split(",") if m.strip()]

    ok = 0
    for mid in model_ids:
        if download_model(mid, output_dir):
            ok += 1

    print(f"\n{ok}/{len(model_ids)} Modelle heruntergeladen nach {output_dir}")
    print("Nächster Schritt: Dateien nach Scout /share/openwakeword kopieren (Samba oder setup_scout_wake_words.py)")
    return 0 if ok == len(model_ids) else 1


if __name__ == "__main__":
    sys.exit(main())
