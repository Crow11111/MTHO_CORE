# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Voice Listener - Continuous voice input for Windows.

Listens via Razer Seiren, uses HA Assist Pipeline for:
1. Wake Word detection (openWakeWord on Scout)
2. Speech-to-Text (Whisper on Scout)
3. CORE processing
4. TTS response (ElevenLabs via Scout → Mini)

Usage:
  python -m src.voice.core_voice_listener

Press Ctrl+C to stop.
"""
import asyncio
import json
import os
import sys
import ssl
import wave
import io
import struct
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import sounddevice as sd
import numpy as np
import websockets
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

# HA Configuration
HA_HOST = os.getenv("HA_HOST_IP", "192.168.178.54")
HA_TOKEN = os.getenv("HASS_TOKEN", "")
PIPELINE_ID = "01hzktez4kncsm0sr1qx32hy5x"

# Audio Configuration  
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_MS = 100  # Send audio in 100ms chunks
RECORD_SECONDS_AFTER_WAKE = 5  # How long to record after wake word

# Wake word simulation (until we have proper Wyoming integration)
WAKE_WORDS = ["computer", "core", "hey core"]


class MthoVoiceListener:
    """Continuous voice listener with wake word detection."""
    
    def __init__(self):
        self.running = False
        self.ws = None
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
    async def connect(self):
        """Connect to HA WebSocket."""
        uri = f"wss://{HA_HOST}:8123/api/websocket"
        self.ws = await websockets.connect(uri, ssl=self.ssl_context)
        
        # Auth
        await self.ws.recv()
        await self.ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        auth_result = await self.ws.recv()
        
        if "auth_ok" in auth_result:
            print("[Connected] HA WebSocket authenticated")
            return True
        else:
            print(f"[Error] Auth failed: {auth_result}")
            return False
    
    async def run_voice_pipeline(self, audio_data: np.ndarray) -> str | None:
        """
        Run the full voice pipeline with audio input.
        
        This uses the HA Assist Pipeline with STT stage.
        """
        if not self.ws:
            await self.connect()
        
        print("[Pipeline] Starting voice pipeline...")
        
        # Start pipeline from STT
        msg_id = int(time.time())
        await self.ws.send(json.dumps({
            "id": msg_id,
            "type": "assist_pipeline/run",
            "start_stage": "stt",
            "end_stage": "tts",
            "input": {
                "sample_rate": SAMPLE_RATE,
            },
            "pipeline": PIPELINE_ID,
        }))
        
        # Wait for stt-start and get binary handler
        handler_id = None
        while True:
            msg = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
            data = json.loads(msg)
            
            if data.get("id") == msg_id and data.get("type") == "result":
                if not data.get("success"):
                    print(f"[Error] Pipeline start failed: {data.get('error')}")
                    return None
            
            event = data.get("event", {})
            event_type = event.get("type", "")
            
            if event_type == "run-start":
                runner_data = event.get("data", {}).get("runner_data", {})
                handler_id = runner_data.get("stt_binary_handler_id")
                print(f"[STT] Binary handler: {handler_id}")
                break
            
            if event_type == "error":
                print(f"[Error] {event}")
                return None
        
        if handler_id:
            # Send audio as binary frames
            # HA expects raw 16-bit PCM in binary WebSocket frames
            # with a 1-byte handler ID prefix
            audio_bytes = audio_data.tobytes()
            
            # Send in chunks (HA recommends ~8KB chunks)
            chunk_size = 8192
            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i:i+chunk_size]
                # Prefix with handler ID (1 byte)
                frame = struct.pack("B", handler_id) + chunk
                await self.ws.send(frame)
            
            # Signal end of audio (empty frame with handler ID)
            await self.ws.send(struct.pack("B", handler_id))
            print("[STT] Audio sent")
        
        # Wait for results
        core_reply = None
        while True:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=30.0)
                
                # Skip binary responses
                if isinstance(msg, bytes):
                    continue
                
                data = json.loads(msg)
                event = data.get("event", {})
                event_type = event.get("type", "")
                
                if event_type == "stt-end":
                    text = event.get("data", {}).get("stt_output", {}).get("text", "")
                    print(f"[STT] Transcribed: {text}")
                
                if event_type == "intent-end":
                    core_reply = event.get("data", {}).get("intent_output", {}).get("response", {}).get("speech", {}).get("plain", {}).get("speech", "")
                    print(f"[CORE] {core_reply}")
                
                if event_type == "tts-end":
                    print("[TTS] Audio generated")
                
                if event_type == "run-end":
                    break
                
                if event_type == "error":
                    print(f"[Error] {event}")
                    break
                    
            except asyncio.TimeoutError:
                print("[Timeout] Pipeline did not complete")
                break
        
        return core_reply
    
    async def listen_continuous(self):
        """
        Continuous listening mode.
        
        Records audio and sends to pipeline.
        For now, uses push-to-talk simulation (records for N seconds).
        
        TODO: Integrate proper wake word detection.
        """
        print("\n" + "="*50)
        print("CORE Voice Listener - Push-to-Talk Mode")
        print("="*50)
        print(f"Microphone: {sd.query_devices(kind='input')['name']}")
        print(f"Pipeline: CORE ({PIPELINE_ID[:8]}...)")
        print("="*50)
        print("\nPress ENTER to start recording (5 seconds)...")
        print("Press Ctrl+C to exit.\n")
        
        await self.connect()
        
        while True:
            try:
                input()  # Wait for Enter
                
                print(f"\n[Recording] Speak now ({RECORD_SECONDS_AFTER_WAKE}s)...")
                
                # Record audio
                audio = sd.rec(
                    int(RECORD_SECONDS_AFTER_WAKE * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    dtype='int16'
                )
                sd.wait()
                
                print("[Recording] Done. Processing...")
                
                # Run pipeline
                result = await self.run_voice_pipeline(audio)
                
                if result:
                    print(f"\n>>> {result}\n")
                
                print("Press ENTER to record again...")
                
            except KeyboardInterrupt:
                print("\n[Exit] Stopping listener...")
                break
            except Exception as e:
                print(f"[Error] {e}")
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()


async def main():
    """Main entry point."""
    listener = MthoVoiceListener()
    
    try:
        await listener.listen_continuous()
    finally:
        await listener.close()


if __name__ == "__main__":
    asyncio.run(main())
