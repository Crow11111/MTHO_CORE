# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Dreadnought Voice Satellite - Windows-based voice input for CORE.

Captures audio from Razer Seiren, detects wake word via openWakeWord (on Scout),
sends transcription to CORE pipeline.

Architecture:
  Razer Seiren -> This Script -> openWakeWord (Scout:10400) -> Whisper (Scout:10300)
                                                            -> CORE Pipeline
"""
import asyncio
import json
import struct
import wave
import io
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sounddevice as sd
import numpy as np
import websockets
import ssl
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

# Configuration
HA_HOST = "192.168.178.54"
HA_TOKEN = os.getenv("HASS_TOKEN", "")
WAKE_WORD_PORT = 10400  # openWakeWord
WHISPER_PORT = 10300    # Whisper STT
PIPELINE_ID = "01hzktez4kncsm0sr1qx32hy5x"  # CORE Pipeline

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.1  # 100ms chunks


class DreadnoughtVoiceSatellite:
    """Windows voice satellite for CORE."""
    
    def __init__(self):
        self.running = False
        self.wake_detected = False
        self.audio_buffer = []
        
    async def connect_wake_word(self):
        """Connect to openWakeWord service."""
        uri = f"tcp://{HA_HOST}:{WAKE_WORD_PORT}"
        print(f"[Wake Word] Connecting to {uri}...")
        # Note: Wyoming protocol uses raw TCP, not WebSocket
        # We'll use the HA WebSocket API instead
        
    async def run_pipeline_with_audio(self, audio_data: bytes):
        """Run CORE pipeline with captured audio."""
        uri = f"wss://{HA_HOST}:8123/api/websocket"
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            # Auth
            await ws.recv()
            await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
            auth_result = await ws.recv()
            
            if "auth_ok" not in auth_result:
                print(f"[Error] Auth failed: {auth_result}")
                return None
            
            # Start pipeline with audio
            await ws.send(json.dumps({
                "id": 1,
                "type": "assist_pipeline/run",
                "start_stage": "stt",
                "end_stage": "tts",
                "input": {
                    "sample_rate": SAMPLE_RATE,
                },
                "pipeline": PIPELINE_ID,
            }))
            
            # Get handler ID
            msg = await ws.recv()
            data = json.loads(msg)
            
            # Wait for stt-start event
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                event_type = data.get("event", {}).get("type", "")
                
                if event_type == "stt-start":
                    handler_id = data["event"]["data"]["runner_data"]["stt_binary_handler_id"]
                    print(f"[STT] Handler ID: {handler_id}")
                    
                    # Send audio in chunks
                    chunk_size = SAMPLE_RATE * 2  # 1 second of 16-bit audio
                    for i in range(0, len(audio_data), chunk_size):
                        chunk = audio_data[i:i+chunk_size]
                        # Binary audio goes to a different handler
                        # This is complex - HA expects binary via WebSocket binary frames
                        pass
                    
                    break
                    
                if event_type == "error":
                    print(f"[Error] {data}")
                    return None
            
            # Collect result
            result = None
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(msg)
                    event_type = data.get("event", {}).get("type", "")
                    
                    if event_type == "intent-end":
                        result = data["event"]["data"]["intent_output"]["response"]["speech"]["plain"]["speech"]
                        print(f"[CORE] {result}")
                    
                    if event_type == "run-end":
                        break
                        
                except asyncio.TimeoutError:
                    break
            
            return result
    
    async def listen_and_detect(self):
        """Main loop: listen for wake word, then capture command."""
        print("[Satellite] Starting voice capture...")
        print(f"[Satellite] Using default microphone: {sd.query_devices(kind='input')['name']}")
        print("[Satellite] Say 'Computer' to activate...")
        
        # For now, we'll use a simple approach:
        # Record 5 seconds and send to pipeline
        duration = 5  # seconds
        
        print(f"\n[Recording] Capturing {duration} seconds...")
        audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, 
                      channels=CHANNELS, dtype='int16')
        sd.wait()
        
        # Convert to bytes
        audio_bytes = audio.tobytes()
        print(f"[Recording] Captured {len(audio_bytes)} bytes")
        
        # For testing, we'll use text-based pipeline instead
        # (Full audio pipeline requires binary WebSocket handling)
        return audio_bytes


async def test_text_pipeline():
    """Test CORE pipeline with text input (simpler)."""
    uri = f"wss://{HA_HOST}:8123/api/websocket"
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with websockets.connect(uri, ssl=ssl_context) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        await ws.recv()
        
        print("[Test] Running text pipeline...")
        await ws.send(json.dumps({
            "id": 1,
            "type": "assist_pipeline/run",
            "start_stage": "intent",
            "end_stage": "tts",
            "input": {"text": "Wie spaet ist es?"},
            "pipeline": PIPELINE_ID,
        }))
        
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            event_type = data.get("event", {}).get("type", "")
            print(f"[Event] {event_type}")
            
            if event_type == "intent-end":
                speech = data["event"]["data"]["intent_output"]["response"]["speech"]["plain"]["speech"]
                print(f"[CORE Reply] {speech}")
            
            if event_type == "run-end":
                break


if __name__ == "__main__":
    print("=== Dreadnought Voice Satellite ===\n")
    
    # Test the text pipeline first
    asyncio.run(test_text_pipeline())
