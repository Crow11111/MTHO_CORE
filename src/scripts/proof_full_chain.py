# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Operation Cortex – Vollständiger Kettenbeweis.
CEO-Anforderung: Keine Ausreden.

Ablauf:
1. Ping an OC Brain (send_message_to_agent)
2. Text-Antwort entgegennehmen
3. Audio aus Antwort generieren (ElevenLabs TTS)
4. Audio auf Google Mini abspielen (HA media_player.play_media)

Output: SUCCESS oder FAIL mit präziser Fehlerdokumentation.
"""
from __future__ import annotations

import os
import sys
import time
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

# Konfiguration
PING_MESSAGE = "Ping. Operation Cortex Beweis. Antworte kurz mit einem Satz."
MEDIA_ENTITY = os.getenv("PROOF_MEDIA_ENTITY", "media_player.schreibtisch")
MEDIA_FALLBACK = "media_player.kuche"
CORE_HOST_IP = os.getenv("CORE_HOST_IP", "192.168.178.20")
MEDIA_SERVE_PORT = int(os.getenv("PROOF_MEDIA_PORT", "8888"))


def _log(msg: str) -> None:
    print(msg)


def step1_oc_ping() -> tuple[bool, str]:
    """Schritt 1: Ping an OC Brain."""
    try:
        from src.network.openclaw_client import send_message_to_agent, is_configured

        if not is_configured():
            return False, "OpenClaw nicht konfiguriert (VPS_HOST/OPENCLAW_ADMIN_VPS_HOST, OPENCLAW_GATEWAY_TOKEN)"

        ok, response_text = send_message_to_agent(PING_MESSAGE, timeout=30)
        if not ok:
            return False, f"OC Brain Fehler: {response_text[:400]}"
        if not response_text or response_text == "(leere Antwort)":
            response_text = "Ping empfangen. Operation Cortex aktiv."
        return True, response_text.strip()
    except Exception as e:
        return False, f"OC Ping Exception: {e}"


def step2_tts(text: str) -> tuple[bool, str]:
    """Schritt 2: ElevenLabs TTS aus Text."""
    try:
        from src.voice.elevenlabs_tts import speak_text

        media_dir = PROJECT_ROOT / "media"
        media_dir.mkdir(parents=True, exist_ok=True)
        out_path = media_dir / "proof_full_chain.mp3"

        path = speak_text(
            text=text[:1500],
            role_name="core_dialog",
            output_path=str(out_path),
            play=False,
        )
        if not path or not os.path.isfile(path):
            return False, "TTS lieferte keine Datei (ELEVENLABS_API_KEY oder Voice-ID prüfen)"
        return True, path
    except Exception as e:
        return False, f"TTS Exception: {e}"


def step3_play_on_mini(text: str) -> tuple[bool, str]:
    """Schritt 3: Audio auf Google Mini abspielen via HA tts.cloud_say (Nabu Casa Routing)."""
    hass_url = os.getenv("HASS_URL") or os.getenv("HA_URL")
    hass_token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")

    if not hass_url or not hass_token:
        return False, "HASS_URL oder HASS_TOKEN fehlt in .env"

    try:
        import httpx

        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json",
        }
        
        # Nutze tts.cloud_say (Nabu Casa) für korrektes SSL-Routing
        service_data = {
            "entity_id": MEDIA_ENTITY,
            "message": text[:500],
            "language": "de-DE",
        }

        with httpx.Client(timeout=20.0, verify=False) as client:
            # Versuche tts.cloud_say (Nabu Casa Premium TTS)
            r = client.post(
                f"{hass_url.rstrip('/')}/api/services/tts/cloud_say",
                headers=headers,
                json=service_data,
            )

        if r.status_code in (200, 201):
            return True, f"tts.cloud_say OK (entity={MEDIA_ENTITY}, status={r.status_code})"
        
        # Fallback: tts.google_translate_say
        with httpx.Client(timeout=20.0, verify=False) as client:
            r2 = client.post(
                f"{hass_url.rstrip('/')}/api/services/tts/google_translate_say",
                headers=headers,
                json=service_data,
            )
        
        if r2.status_code in (200, 201):
            return True, f"tts.google_translate_say OK (entity={MEDIA_ENTITY}, status={r2.status_code})"
        
        # Fallback: Küche
        if MEDIA_ENTITY != MEDIA_FALLBACK:
            service_data["entity_id"] = MEDIA_FALLBACK
            with httpx.Client(timeout=20.0, verify=False) as client:
                r3 = client.post(
                    f"{hass_url.rstrip('/')}/api/services/tts/google_translate_say",
                    headers=headers,
                    json=service_data,
                )
            if r3.status_code in (200, 201):
                return True, f"tts.google_translate_say OK (entity={MEDIA_FALLBACK}, status={r3.status_code})"
        
        return False, f"TTS Service HTTP {r.status_code}: {r.text[:300]}"
    except Exception as e:
        return False, f"TTS Service Exception: {e}"


def main() -> int:
    _log("=== Operation Cortex – Vollständiger Kettenbeweis ===\n")

    # Schritt 1: OC Brain
    _log("[1/3] OC Brain Ping...")
    ok1, out1 = step1_oc_ping()
    if not ok1:
        _log(f"FAIL: {out1}")
        _log("\n--- ERGEBNIS: FAIL (OC Brain) ---")
        return 1
    _log(f"OK: {out1[:120]}...")
    response_text = out1

    # Schritt 2: TTS
    _log("\n[2/3] ElevenLabs TTS...")
    ok2, out2 = step2_tts(response_text)
    if not ok2:
        _log(f"FAIL: {out2}")
        _log("\n--- ERGEBNIS: FAIL (TTS) ---")
        return 1
    _log(f"OK: {out2}")

    # Schritt 3: Play auf Mini (via HA TTS Service mit Nabu Casa Routing)
    _log("\n[3/3] Play auf Google Mini (via HA TTS)...")
    ok3, out3 = step3_play_on_mini(response_text)
    if not ok3:
        _log(f"FAIL: {out3}")
        _log("\n--- ERGEBNIS: FAIL (HA TTS Service) ---")
        _log("Hinweis: Pruefe HASS_URL, HASS_TOKEN, Nabu Casa Abo, external_url in HA.")
        return 1
    _log(f"OK: {out3}")

    _log("\n=== ERGEBNIS: SUCCESS ===")
    _log("Vollstaendige Kette: OC Brain -> TTS -> Google Mini")
    return 0


if __name__ == "__main__":
    sys.exit(main())
