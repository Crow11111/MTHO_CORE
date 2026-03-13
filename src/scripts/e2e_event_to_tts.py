# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Z13 E2E: Event → OC Brain → Antwort → TTS (MP3).
Sensorik-I/O: Ein Event rein, gesprochene Antwort raus.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def main() -> int:
    parser = argparse.ArgumentParser(description="E2E: Event an OC Brain, Antwort als TTS speichern")
    parser.add_argument("--type", default="e2e_test", help="event_type")
    parser.add_argument("--node", default="dreadnought", help="node_id")
    parser.add_argument("--role", default="core_dialog", help="TTS-Rolle")
    parser.add_argument("--out", default=None, help="MP3-Ausgabepfad (default: media/e2e_<id>.mp3)")
    args = parser.parse_args()

    event = {
        "source": "e2e_script",
        "node_id": args.node,
        "event_type": args.type,
        "data": {},
    }

    from src.network.openclaw_client import send_event_to_oc_brain, is_configured
    if not is_configured():
        print("FAIL: OpenClaw nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN)")
        return 1

    ok, response_text = send_event_to_oc_brain(event, timeout=30)
    if not ok:
        print(f"FAIL: OC Brain: {response_text[:300]}")
        return 1
    if not response_text or response_text == "(leere Antwort)":
        response_text = "Event empfangen. Keine weitere Antwort."

    from src.voice.elevenlabs_tts import speak_text
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_path = args.out or os.path.join(root, "media", f"e2e_{uuid.uuid4().hex[:12]}.mp3")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    path = speak_text(
        text=response_text[:1500],
        role_name=args.role,
        output_path=out_path,
        play=False,
    )
    if not path or not os.path.isfile(path):
        print("FAIL: TTS fehlgeschlagen (Voice-ID oder API-Key)")
        return 1
    print(f"OK: Event->OC->TTS | {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
