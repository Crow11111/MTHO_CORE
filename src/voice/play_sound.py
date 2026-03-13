# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Voice – Sound-Abspiel auf Mini
====================================
Spielt Audio-Dateien (MP3) auf HA media_player (z.B. Google Mini).
Nutzt HTTP-Server + media_player.play_media wie tts_dispatcher.
"""
from __future__ import annotations

import asyncio
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

from loguru import logger

from dotenv import load_dotenv

load_dotenv()

DEFAULT_ENTITY = "media_player.schreibtisch"
DEFAULT_STREAM_PORT = 8002


async def play_sound_on_mini(
    file_path: str,
    entity_id: str | None = None,
    port: int | None = None,
) -> bool:
    """
    Spielt Audio-Datei auf Mini-Speaker via HA media_player.play_media.

    Args:
        file_path: Pfad zur MP3/WAV-Datei (absolut oder relativ zu CWD)
        entity_id: HA media_player Entity (Default: TTS_CONFIRMATION_ENTITY)
        port: HTTP-Port für temporären Server (Default: TTS_STREAM_PORT)

    Returns:
        True bei Erfolg, False bei Fehler.
    """
    path = os.path.abspath(file_path)
    if not os.path.isfile(path):
        logger.warning("play_sound_on_mini: Datei nicht gefunden: {}", path)
        return False

    hass_url = os.getenv("HASS_URL") or os.getenv("HA_URL")
    hass_token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
    if not hass_url or not hass_token:
        logger.warning("HASS_URL/TOKEN fehlt – spiele lokal ab.")
        await asyncio.to_thread(os.startfile, path)
        return True

    host_ip = os.getenv("CORE_HOST_IP", "192.168.178.20")
    port = port or int(os.getenv("TTS_STREAM_PORT", str(DEFAULT_STREAM_PORT)))
    entity_id = (
        entity_id
        or os.getenv("TTS_CONFIRMATION_ENTITY", DEFAULT_ENTITY).strip()
        or DEFAULT_ENTITY
    )
    filename = os.path.basename(path)
    serve_dir = os.path.dirname(path)
    audio_url = f"http://{host_ip}:{port}/{filename}"

    server_done = asyncio.Event()
    server_obj: list = [None]

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
            logger.info("Sound auf Mini gestartet: {}", filename)
        else:
            logger.warning("HA play_media fehlgeschlagen.")
        await asyncio.sleep(5)
        return result is not None
    finally:
        if server_obj[0]:
            server_obj[0].shutdown()
