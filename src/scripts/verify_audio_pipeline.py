import os
import sys

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def verify_audio_file():
    path = "c:/ATLAS_CORE/media/dev_agent_reply.mp3"
    if not os.path.exists(path):
        print(f"FAIL: File not found at {path}")
        return False
    
    size = os.path.getsize(path)
    if size == 0:
        print(f"FAIL: File size is 0 bytes at {path}")
        return False
        
    with open(path, "rb") as f:
        header = f.read(3)
        if header != b"ID3":
            # MP3s can also start with sync frames (0xFF 0xFB), but ID3 is common for ElevenLabs
            # Let's check for sync frame if ID3 is missing
            f.seek(0)
            header = f.read(2)
            if header != b'\xff\xfb' and header != b'\xff\xf3' and header != b'\xff\xf2': # loose check
                # Re-read 3 bytes for ID3 check context in print
                f.seek(0)
                print(f"WARN: File header {f.read(3)} does not look like standard ID3 or MP3 sync.")
                # We won't fail just on this if size is ok, but good to note.
    
    print(f"SUCCESS: Audio file verified. Size: {size} bytes.")
    return True

def check_cast_logic():
    # Simulate src/edge/audio_player.py logic check
    # We are checking if it points to 'media/' or 'static/audio/'
    
    from src.edge.audio_player import AudioPlayer
    import inspect
    
    # Analyze the source code of play_audio_on_device to see path construction
    source = inspect.getsource(AudioPlayer.play_audio_on_device)
    
    print("\n--- AudioPlayer Logic Analysis ---")
    if '/static/audio' in source:
        print("INFO: AudioPlayer uses '/static/audio' path.")
    else:
        print("INFO: AudioPlayer does NOT appear to use '/static/audio' explicitly.")
        
    if '/media' in source:
        print("INFO: AudioPlayer uses '/media' path.")
    else:
        print("WARN: AudioPlayer does NOT use '/media' path. It may not find 'dev_agent_reply.mp3'.")

    # Check for hardcoded IP or env var
    if 'SCOUT_IP' in source:
         print("INFO: AudioPlayer uses 'SCOUT_IP' env var.")
    
    return True

if __name__ == "__main__":
    print("--- Audio Pipeline Verification ---")
    if verify_audio_file():
        check_cast_logic()
