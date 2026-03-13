# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
Test-Script für ElevenLabs TTS Integration (CORE Voice Assistant).

Prüft:
1. ElevenLabs API-Key und lokale Wiedergabe (target=elevenlabs)
2. Optional: Stream zu HA Mini (target=elevenlabs_stream)
3. Fallback: Piper oder mini wenn ElevenLabs nicht verfügbar

Verwendung:
  python -m src.scripts.test_elevenlabs_output                    # Lokal
  python -m src.scripts.test_elevenlabs_output --stream            # Stream zu Mini
  python -m src.scripts.test_elevenlabs_output --target mini       # Nur HA TTS
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

# Root-Pfad für Imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")


TEST_TEXT = "Hallo Marc. Ich bin Core. Die ElevenLabs Integration ist bereit."


async def run_test(target: str, role: str = "core_dialog") -> bool:
    from src.voice.tts_dispatcher import dispatch_tts, _elevenlabs_available, _piper_available

    print(f"--- ElevenLabs TTS Test (target={target}, role={role}) ---")
    print(f"Text: {TEST_TEXT[:60]}...")
    print()

    if target in ("elevenlabs", "elevenlabs_stream", "local", "both"):
        if _elevenlabs_available():
            print("[OK] ELEVENLABS_API_KEY gesetzt")
        else:
            print("[WARN] ELEVENLABS_API_KEY fehlt – Fallback auf Piper oder mini")
    if target == "piper" or not _elevenlabs_available():
        if _piper_available():
            print("[OK] Piper TTS verfügbar")
        else:
            print("[WARN] Piper nicht installiert – Fallback auf mini (HA TTS)")

    print()
    ok = await dispatch_tts(text=TEST_TEXT, target=target, role_name=role)
    print()
    print(f"Ergebnis: {'SUCCESS' if ok else 'FAIL'}")
    return ok


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs TTS Test")
    parser.add_argument(
        "--target",
        default="elevenlabs",
        choices=["mini", "elevenlabs", "elevenlabs_stream", "local", "both", "piper"],
        help="Ziel: elevenlabs (lokal), elevenlabs_stream (Mini), mini, both, piper",
    )
    parser.add_argument(
        "--role",
        default="core_dialog",
        help="Rolle aus voice_config (core_dialog, analyst, therapeut, ...)",
    )
    args = parser.parse_args()

    ok = asyncio.run(run_test(target=args.target, role=args.role))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
