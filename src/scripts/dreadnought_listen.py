# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Dreadnought Listen: Aufnahme → Transkription (lokal Gemini) → OC Brain (Text) → TTS → Mini.

Fix: OC Brain (VPS) kann lokale Dateien nicht lesen. Daher:
1. WAV lokal mit Gemini transkribieren
2. Text (nicht audio_path) an OC Brain senden
3. OC-Antwort → ElevenLabs TTS → media_player.schreibtisch
"""
import os
import sys
import wave
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timezone

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def _write_dummy_wav(filename: str, reason: str) -> str:
    """Schreibt explizit markierte Dummy-WAV (Filename + 1 Sample != 0 als Marker)."""
    base, name = os.path.split(filename)
    if not name.lower().startswith("dummy_"):
        filename = os.path.join(base, "dummy_" + name)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        frames = b'\x00' * (44100 * 2 - 2) + b'\x01\x00'
        wf.writeframes(frames)
    return os.path.abspath(filename)


def record_audio(duration: int = 7, filename: str = "voice_input.wav") -> tuple[str | None, str, str]:
    """
    Returns: (abs_path | None, "real" | "dummy", detail_message).
    """
    try:
        import sounddevice as sd
        import numpy as np

        fs = 44100
        log(f"Starte Aufnahme ({duration}s)...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        log("Aufnahme beendet.")

        audio_int16 = (recording * 32767).astype(np.int16)
        max_amp = int(np.max(np.abs(audio_int16)))

        if max_amp == 0:
            log("Aufnahme enthält nur Nullen (kein Signal). Schreibe dokumentierten Dummy.")
            path = _write_dummy_wav(filename, "Keine Amplituden – Stille oder falsches Gerät")
            return path, "dummy", "Keine Amplituden (Stille/kein Gerät)"

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_int16.tobytes())
        return os.path.abspath(filename), "real", f"Reale Aufnahme (max_amp={max_amp})"
    except Exception as e:
        log(f"Hardware/Treiber Fehler: {e}. Schreibe dokumentierten Dummy.")
        path = _write_dummy_wav(filename, str(e))
        return path, "dummy", f"Exception: {e}"


def verify_wav_has_samples(wav_path: str) -> tuple[bool, str]:
    """Prüft ob WAV reale Amplituden hat (≠0). Return (ok, detail)."""
    try:
        import numpy as np
        with wave.open(wav_path, 'rb') as wf:
            buf = wf.readframes(wf.getnframes())
        arr = np.frombuffer(buf, dtype=np.int16)
        max_amp = int(np.max(np.abs(arr))) if len(arr) else 0
        if max_amp > 0:
            return True, f"max_amp={max_amp}"
        return False, "keine Amplituden (alles Null)"
    except Exception as e:
        return False, str(e)[:80]


def transcribe_wav(wav_path: str) -> str:
    """Transkribiert WAV lokal mit Gemini. Nutzt transcribe_audio_batch."""
    try:
        from src.scripts.transcribe_audio_batch import transcribe_wav as _transcribe
        return _transcribe(wav_path).strip()
    except Exception as e:
        log(f"[FAIL] Transkription: {e}")
        return ""


def send_event(audio_path: str) -> bool:
    """
    Legacy: Transkribiert WAV, sendet Text an OC Brain, spielt Antwort auf Mini.
    (OC Brain kann lokale Dateien nicht lesen – daher Transkription vor dem Senden.)
    """
    transcript = transcribe_wav(audio_path)
    return send_text_to_oc_and_play_response(transcript)


def send_text_to_oc_and_play_response(text: str) -> bool:
    """
    Sendet Text an OC Brain, empfängt Antwort, spielt via ElevenLabs TTS auf Mini.
    """
    try:
        from src.network.openclaw_client import send_message_to_agent, is_configured
        from src.voice.elevenlabs_tts import speak_text
        from src.network.ha_client import HAClient

        if not is_configured():
            log("[FAIL] OpenClaw Client nicht konfiguriert.")
            return False

        # Fallback bei leerer Transkription (z.B. Dummy/Stille)
        if not text or len(text.strip()) < 2:
            text = "Axiom: CORE hört (Test-Input)."
            log(f"[INFO] Leere Transkription, nutze Fallback: {text}")

        log(f"[OC] Sende Text ({len(text)} Zeichen)...")
        success, response_text = send_message_to_agent(text, timeout=30)
        if not success:
            log(f"[FAIL] OC Brain: {response_text[:300]}")
            return False
        if not response_text or response_text == "(leere Antwort)":
            response_text = "Empfangen. Keine weitere Antwort."

        log(f"[OC] Antwort: {response_text[:80]}...")

        # TTS via ElevenLabs
        media_dir = os.path.join(os.getcwd(), "media")
        os.makedirs(media_dir, exist_ok=True)
        mp3_path = os.path.join(media_dir, f"dreadnought_reply_{int(time.time())}.mp3")

        path = speak_text(
            text=response_text[:1500],
            role_name="core_dialog",
            output_path=mp3_path,
            play=False,
        )
        if not path or not os.path.isfile(path):
            log("[FAIL] TTS lieferte keine Datei.")
            return False

        # Play auf Mini via HA media_player.play_media (HTTP-Server wie send_whatsapp_audio)
        hass_url = os.getenv("HASS_URL") or os.getenv("HA_URL")
        hass_token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
        host_ip = os.getenv("CORE_HOST_IP", "192.168.178.20")
        port = 8002
        filename = os.path.basename(path)
        serve_dir = os.path.dirname(os.path.abspath(path))
        audio_url = f"http://{host_ip}:{port}/{filename}"

        if hass_url and hass_token:
            orig_dir = os.getcwd()
            os.chdir(serve_dir)
            server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
            t = threading.Thread(target=server.serve_forever)
            t.daemon = True
            t.start()
            time.sleep(0.5)
            try:
                ok = HAClient().call_service(
                    "media_player",
                    "play_media",
                    service_data={
                        "entity_id": os.getenv("DREADNOUGHT_MEDIA_ENTITY", "media_player.schreibtisch"),
                        "media_content_id": audio_url,
                        "media_content_type": "music",
                    },
                )
                if ok:
                    log("[SUCCESS] Antwort auf Mini abgespielt.")
                else:
                    log("[FAIL] HA play_media fehlgeschlagen.")
            finally:
                time.sleep(8)  # Mini braucht Zeit zum Streamen
                server.shutdown()
                os.chdir(orig_dir)
        else:
            log("[WARN] HASS_URL/TOKEN fehlt – TTS-Datei erzeugt, aber nicht auf Mini abgespielt.")
            log(f"Datei: {path}")

        return True
    except Exception as e:
        log(f"[FAIL] Interner Fehler: {e}")
        return False


if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    if len(sys.argv) >= 3 and sys.argv[1] == "verify":
        ok, detail = verify_wav_has_samples(sys.argv[2])
        print(f"Verifizierung: {'OK' if ok else 'FAIL'} – {detail}")
        sys.exit(0 if ok else 1)

    audio_file = f"media/voice_input_{int(time.time())}.wav"
    os.makedirs("media", exist_ok=True)

    path, mode, msg = record_audio(duration=5, filename=audio_file)
    if not path:
        print("\n[FAIL: Aufnahme fehlgeschlagen]")
        sys.exit(1)

    if mode == "dummy":
        print(f"\n[DUMMY] {msg}")

    # Transkribieren (lokal Gemini)
    log("Transkribiere WAV...")
    transcript = transcribe_wav(path)
    if transcript:
        log(f"Transkription: {transcript[:100]}...")
    else:
        log("Transkription leer (Stille/Dummy) – nutze Fallback.")

    # Text an OC Brain → Antwort → TTS → Mini
    if send_text_to_oc_and_play_response(transcript):
        print("\n[SUCCESS] Recording → Transkription → OC Brain → TTS → Mini")
    else:
        print("\n[FAIL: Senden oder TTS fehlerhaft]")
        sys.exit(1)
