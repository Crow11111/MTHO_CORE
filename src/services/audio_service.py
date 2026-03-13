# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

VOICE_MAP = {
    "default": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "calm": "EXAVITQu4vr4xnSDxMaL",     # Bella
    "strict": "ErXwobaYiN019PkySvjV",   # Antoni
}

class AudioService:
    def __init__(self):
        self._api_key = os.getenv("ELEVENLABS_API_KEY")
        self._base_url = "https://api.elevenlabs.io/v1/text-to-speech"

    async def generate_speech(self, text: str, role: str = "default") -> bytes:
        if not self._api_key:
            self._api_key = os.getenv("ELEVENLABS_API_KEY")
            if not self._api_key:
                logger.error("ELEVENLABS_API_KEY fehlt in .env")
                return b""
        
        voice_id = VOICE_MAP.get(role, VOICE_MAP["default"])
        url = f"{self._base_url}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self._api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.content
            except Exception as e:
                logger.error(f"Fehler bei Audio-Generierung: {e}")
                return b""

audio_service = AudioService()
