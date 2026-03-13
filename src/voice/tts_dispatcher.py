# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
TTS-Dispatcher: Verteilt TTS an Mini (HA), ElevenLabs (lokal/Stream) oder Piper (Fallback).

SCOUT-FUSION Update: HA-Piper-Remote (Wyoming) als Failover-Option

Targets:
- mini: HA TTS (google_translate_say) auf media_player
- elevenlabs: ElevenLabs lokal auf PC (os.startfile)
- elevenlabs_stream: ElevenLabs → MP3 → HA media_player.play_media (Stream zu Mini)
- both: mini + elevenlabs parallel
- piper: Piper TTS lokal (Fallback wenn ElevenLabs nicht verfuegbar)
- ha_piper: HA Piper (Wyoming auf Scout) - Remote TTS

Fallback-Kette: elevenlabs* → Piper (lokal) → ha_piper (Remote) → mini (HA TTS)
"""
from __future__ import annotations

import asyncio
import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional

from loguru import logger

from dotenv import load_dotenv

load_dotenv()


DEFAULT_ENTITY = "media_player.schreibtisch"
DEFAULT_STREAM_PORT = 8002
# CORE-Default-Stimme (core_dialog aus voice_config)
DEFAULT_CORE_VOICE_ID = "0ISBUrWf7OGBgepl5lu2"


def _elevenlabs_available() -> bool:
    """Prüft ob ElevenLabs API-Key gesetzt ist."""
    return bool(os.getenv("ELEVENLABS_API_KEY", "").strip())


def _piper_available() -> bool:
    """Prüft ob Piper TTS verfügbar ist (Paket + Stimmenmodell via PIPER_VOICE_PATH)."""
    try:
        from piper import PiperVoice  # noqa: F401
        voice_path = os.getenv("PIPER_VOICE_PATH", "").strip()
        if voice_path and os.path.isfile(voice_path):
            return True
        # Typische Piper-Stimmen (piper-tts download_voices)
        base = os.path.join(os.path.expanduser("~"), ".local", "share", "piper", "voices")
        if os.path.isdir(base):
            for root, _, files in os.walk(base):
                if any(f.endswith(".onnx") for f in files):
                    return True
        return False
    except ImportError:
        return False


async def _elevenlabs_speak(
    text: str,
    role_name: str = "core_dialog",
    output_path: Optional[str] = None,
    play: bool = True,
) -> Optional[str]:
    """ElevenLabs TTS – gibt Dateipfad zurück oder None bei Fehler."""
    try:
        from src.voice.elevenlabs_tts import speak_text

        voice_override = os.getenv("ELEVENLABS_VOICE_ID", "").strip() or None
        path = await asyncio.to_thread(
            speak_text,
            text,
            role_name,
            "",
            output_path,
            play,
            override_voice_id=voice_override,
        )
        return path
    except Exception as e:
        logger.error(f"ElevenLabs TTS fehlgeschlagen: {e}")
        return None


def _find_piper_voice_path() -> Optional[str]:
    """Sucht Piper-Stimmenmodell (.onnx)."""
    voice_path = os.getenv("PIPER_VOICE_PATH", "").strip()
    if voice_path and os.path.isfile(voice_path):
        return voice_path
    base = os.path.join(os.path.expanduser("~"), ".local", "share", "piper", "voices")
    if not os.path.isdir(base):
        return None
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".onnx"):
                return os.path.join(root, f)
    return None


async def _piper_speak(text: str, play: bool = True) -> Optional[str]:
    """Piper TTS (lokal) – Fallback wenn ElevenLabs nicht verfügbar."""
    try:
        from piper import PiperVoice
        import wave

        voice_path = _find_piper_voice_path()
        if not voice_path:
            logger.warning(
                "Piper: Kein Stimmenmodell. PIPER_VOICE_PATH setzen oder "
                "python -m piper.download_voices de_DE-lessac-medium ausführen."
            )
            return None

        media_dir = os.path.join(os.getcwd(), "media")
        os.makedirs(media_dir, exist_ok=True)
        out_path = os.path.join(media_dir, f"piper_fallback_{int(time.time())}.wav")

        def _run():
            voice = PiperVoice.load(voice_path)
            with wave.open(out_path, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file)

        await asyncio.to_thread(_run)
        if play and os.path.isfile(out_path):
            await asyncio.to_thread(os.startfile, out_path)
        return out_path
    except ImportError:
        logger.warning("Piper TTS nicht installiert (pip install piper-tts).")
        return None
    except Exception as e:
        logger.error(f"Piper TTS fehlgeschlagen: {e}")
        return None


async def _mini_tts(text: str) -> bool:
    """HA TTS (google_translate_say / cloud_say) auf media_player."""
    entity_id = (
        os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip() or DEFAULT_ENTITY
    )
    try:
        from src.connectors.home_assistant import HomeAssistantClient

        client = HomeAssistantClient()
        result = await client.call_service(
            "tts",
            "google_translate_say",
            {"entity_id": entity_id, "message": text},
        )
        if result is None:
            result = await client.call_service(
                "tts", "cloud_say", {"entity_id": entity_id, "message": text}
            )
        return result is not None
    except Exception as e:
        logger.error(f"TTS mini fehlgeschlagen: {e}")
        return False


async def _ha_piper_tts(text: str) -> bool:
    """
    HA Piper TTS (Wyoming auf Scout) - Remote TTS Failover.
    Nutzt tts.speak mit HA Piper Entity.
    """
    entity_id = (
        os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip() or DEFAULT_ENTITY
    )
    piper_entity = os.getenv("HA_PIPER_ENTITY", "tts.piper").strip()
    try:
        from src.connectors.home_assistant import HomeAssistantClient

        client = HomeAssistantClient()
        result = await client.call_service(
            "tts",
            "speak",
            {
                "entity_id": piper_entity,
                "media_player_entity_id": entity_id,
                "message": text,
            },
        )
        if result is not None:
            logger.info(f"HA Piper TTS erfolgreich auf {entity_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"HA Piper TTS fehlgeschlagen: {e}")
        return False


async def _elevenlabs_stream_to_mini(
    text: str,
    role_name: str = "core_dialog",
) -> bool:
    """
    ElevenLabs → MP3 → temporärer HTTP-Server → HA media_player.play_media.
    Der Mini streamt die MP3 von CORE_HOST_IP:PORT.
    """
    path = await _elevenlabs_speak(
        text, role_name, output_path=None, play=False
    )
    if not path or not os.path.isfile(path):
        logger.warning("ElevenLabs Stream: Keine Audio-Datei, Fallback auf Piper oder mini.")
        if _piper_available():
            path = await _piper_speak(text, play=False)
        if not path or not os.path.isfile(path):
            return await _mini_tts(text)

    hass_url = os.getenv("HASS_URL") or os.getenv("HA_URL")
    hass_token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
    if not hass_url or not hass_token:
        logger.warning("HASS_URL/TOKEN fehlt – spiele lokal ab.")
        await asyncio.to_thread(os.startfile, path)
        return True

    host_ip = os.getenv("CORE_HOST_IP", "192.168.178.20")
    port = int(os.getenv("TTS_STREAM_PORT", str(DEFAULT_STREAM_PORT)))
    filename = os.path.basename(path)
    serve_dir = os.path.dirname(os.path.abspath(path))
    audio_url = f"http://{host_ip}:{port}/{filename}"
    entity_id = (
        os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip() or DEFAULT_ENTITY
    )

    server_done = asyncio.Event()
    server_obj = [None]  # Mutable für Zugriff aus Thread

    def _serve():
        orig_dir = os.getcwd()
        os.chdir(serve_dir)
        server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
        server_obj[0] = server
        server_done.set()
        server.serve_forever()
        os.chdir(orig_dir)

    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    await server_done.wait()
    await asyncio.sleep(0.5)

    try:
        from src.connectors.home_assistant import HomeAssistantClient

        client = HomeAssistantClient()
        result = await client.call_service(
            "media_player",
            "play_media",
            {
                "entity_id": entity_id,
                "media_content_id": audio_url,
                "media_content_type": "music",
            },
        )
        if result is not None:
            logger.info("ElevenLabs Stream: Audio auf Mini gestartet.")
        else:
            logger.warning("HA play_media fehlgeschlagen.")
        # Mini braucht Zeit zum Streamen
        await asyncio.sleep(8)
        return result is not None
    finally:
        if server_obj[0]:
            server_obj[0].shutdown()


async def dispatch_tts(
    text: str,
    target: str = "mini",
    role_name: str = "core_dialog",
) -> bool:
    """
    Spielt TTS ab.

    Targets:
    - mini: HA TTS (google_translate_say) auf media_player
    - elevenlabs: ElevenLabs lokal (Fallback: Piper → mini)
    - elevenlabs_stream: ElevenLabs → HA media_player.play_media (Fallback: Piper → mini)
    - both: mini + elevenlabs parallel
    - piper: Piper TTS lokal (nur wenn Piper installiert)
    """
    text = (text or "").strip()
    if not text:
        logger.warning("dispatch_tts: leerer Text, überspringe.")
        return False

    target = (target or "mini").lower()

    async def _local_elevenlabs() -> bool:
        if _elevenlabs_available():
            path = await _elevenlabs_speak(text, role_name, play=True)
            if path:
                return True
        # Scout-Prefer: Versuche erst HA Piper (Remote), dann lokales Piper
        if await _ha_piper_tts(text):
            return True
        if _piper_available():
            path = await _piper_speak(text, play=True)
            if path:
                return True
        return await _mini_tts(text)

    async def _stream_elevenlabs() -> bool:
        if _elevenlabs_available():
            return await _elevenlabs_stream_to_mini(text, role_name)
        if _piper_available():
            path = await _piper_speak(text, play=True)
            if path:
                return True
        return await _mini_tts(text)

    if target == "mini":
        return await _mini_tts(text)

    if target == "elevenlabs" or target == "local":
        return await _local_elevenlabs()

    if target == "elevenlabs_stream":
        return await _stream_elevenlabs()

    if target == "both":
        ok_mini, ok_local = await asyncio.gather(
            _mini_tts(text), _local_elevenlabs()
        )
        return ok_mini or ok_local

    if target == "piper":
        if _piper_available():
            path = await _piper_speak(text, play=True)
            return path is not None
        logger.warning("Piper lokal nicht verfuegbar, versuche HA Piper (Remote).")
        if await _ha_piper_tts(text):
            return True
        logger.warning("HA Piper auch nicht verfuegbar, Fallback auf mini.")
        return await _mini_tts(text)

    if target == "ha_piper":
        if await _ha_piper_tts(text):
            return True
        logger.warning("HA Piper nicht verfuegbar, Fallback auf mini.")
        return await _mini_tts(text)

    logger.warning(f"dispatch_tts: unbekanntes target='{target}', nutze mini.")
    return await _mini_tts(text)
