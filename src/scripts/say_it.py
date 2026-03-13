import sys
import os
import asyncio
import argparse

# Sicherstellen, dass Encoding stimmt (Windows PowerShell Fix)
sys.stdout.reconfigure(encoding='utf-8')

# Füge Project Root zum Pfad hinzu, falls nötig
sys.path.append(os.getcwd())

# Import
try:
    from src.voice.tts_dispatcher import dispatch_tts
except ImportError:
    # Fallback falls Aufruf nicht aus Root erfolgt
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.voice.tts_dispatcher import dispatch_tts

async def main():
    parser = argparse.ArgumentParser(description="CORE TTS CLI Wrapper")
    parser.add_argument("text", type=str, help="Text to speak")
    parser.add_argument("--target", "-t", type=str, default="mini", help="Target device (mini, elevenlabs, etc.)")
    parser.add_argument("--role", "-r", type=str, default="core_dialog", help="Role name (for ElevenLabs)")
    
    args = parser.parse_args()
    
    print(f"Spreche: '{args.text}' auf Target: {args.target}...")
    try:
        success = await dispatch_tts(args.text, target=args.target, role_name=args.role)
        if success:
            print("✅ TTS dispatched.")
            sys.exit(0)
        else:
            print("❌ TTS failed.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
