# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import os
import pychromecast
from loguru import logger
from src.services.audio_service import AudioService

# Initialize Audio Service
audio_service = AudioService()

class AudioPlayer:
    def __init__(self):
        self.chromecasts = {}
        self.browser = None

    def discover_devices(self):
        """Scans network for Cast devices (needs network_mode: host)."""
        logger.info("Discovering Cast devices...")
        services, browser = pychromecast.discovery.discover_chromecasts()
        pychromecast.discovery.stop_discovery(browser)
        
        self.chromecasts = {c.device.friendly_name: c for c in services}
        logger.info(f"Found devices: {list(self.chromecasts.keys())}")
        return self.chromecasts

    async def play_audio_on_device(self, device_name: str, text: str, role: str = "default"):
        """Generates audio via ElevenLabs and casts it to the specified device."""
        if not self.chromecasts:
            self.discover_devices()

        cast = self.chromecasts.get(device_name)
        if not cast:
            logger.error(f"Device '{device_name}' not found. Available: {list(self.chromecasts.keys())}")
            return False

        # Generate Audio
        logger.info(f"Generating audio for role '{role}'...")
        audio_data = await audio_service.generate_speech(text, role)
        
        if not audio_data:
            logger.error("Audio generation failed.")
            return False

        # Save to temporary file accessible via HTTP
        # Note: In a real deployment, we need a web server to serve this file.
        # For now, we assume the Scout runs a simple HTTP server or shares a volume.
        # Alternatively, we can use pychromecast to play a publicly accessible URL if we upload it.
        # But keeping it local is better.
        # Let's save it to a static directory.
        output_dir = "/app/static/audio"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"speech_{hash(text)}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(audio_data)
        
        # Construct URL (assuming Scout IP is reachable by Nest Mini)
        # We need the Scout's IP.
        # For now, placeholder.
        scout_ip = os.getenv("SCOUT_IP", "192.168.178.XX") # Needs configuration
        audio_url = f"http://{scout_ip}:8000/static/audio/{filename}"
        
        logger.info(f"Casting to {device_name}: {audio_url}")
        
        cast.wait()
        mc = cast.media_controller
        mc.play_media(audio_url, 'audio/mp3')
        mc.block_until_active()
        return True

if __name__ == "__main__":
    # Test script
    player = AudioPlayer()
    # Example usage:
    # asyncio.run(player.play_audio_on_device("Google Nest Mini", "Hallo Marc, System bereit.", "default"))
