# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Sprechen testen: TTS (ElevenLabs) und/oder WhatsApp via HA (Scout).
Ausgabe: Audio-Datei auf Dreadnought und/oder Nachricht an WHATSAPP_TARGET_ID.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")

DEFAULT_MESSAGE = "CORE Prototyp 0.5. Scout wieder online. Sehen, Hoeren, Sprechen – Test."


def main():
    msg = os.getenv("CORE_SPEAK_MESSAGE", DEFAULT_MESSAGE)
    out = []

    # 1) TTS (wenn ELEVENLABS_API_KEY)
    if os.getenv("ELEVENLABS_API_KEY"):
        try:
            from src.voice.elevenlabs_tts import speak_text
            path = speak_text(msg, role_name="core_dialog", output_path=None, play=False)
            if path:
                out.append(("TTS", "OK", path))
            else:
                out.append(("TTS", "FAIL", "speak_text returned None"))
        except Exception as e:
            out.append(("TTS", "FAIL", str(e)[:100]))
    else:
        out.append(("TTS", "SKIP", "ELEVENLABS_API_KEY fehlt"))

    # 2) WhatsApp via HA (Scout/Dreadnought)
    target = os.getenv("WHATSAPP_TARGET_ID", "").strip().strip('"')
    if target and os.getenv("HASS_URL") and os.getenv("HASS_TOKEN"):
        try:
            from src.network.ha_client import HAClient
            ok = HAClient().send_whatsapp(to_number=target, text=f"[CORE] {msg}")
            out.append(("WhatsApp (HA)", "OK" if ok else "FAIL", target))
        except Exception as e:
            out.append(("WhatsApp (HA)", "FAIL", str(e)[:80]))
    else:
        out.append(("WhatsApp (HA)", "SKIP", "HASS_URL/HASS_TOKEN/WHATSAPP_TARGET_ID fehlt"))

    for name, status, detail in out:
        print(f"{name}: {status} {detail}")
    return 0 if any(o[1] == "OK" for o in out) else 1


if __name__ == "__main__":
    sys.exit(main())
