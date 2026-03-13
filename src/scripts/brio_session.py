# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import requests
import time
import os

def capture_brio_snapshot(stream_name="pc", base_url="http://localhost:1984"):
    mjpeg_url = f"{base_url}/api/stream.mjpeg?src={stream_name}"
    frame_url = f"{base_url}/api/frame.jpeg?src={stream_name}"
    output_path = "brio_session_test.jpg"
    
    print(f"Starte Brio Session für Stream '{stream_name}'...")
    
    try:
        # 1. Öffne den MJPEG Stream persistent im Hintergrund
        with requests.get(mjpeg_url, stream=True, timeout=15) as mjpeg_r:
            print("MJPEG Stream angefordert. Warte auf Hardware-Initialisierung (LED)...")
            
            # Wir lesen nur ein bisschen vom Stream, um sicherzustellen, dass er läuft
            count = 0
            for chunk in mjpeg_r.iter_content(chunk_size=1024):
                if chunk:
                    count += 1
                    if count > 5: # Etwa 5KB empfangen
                        print("Stream läuft! Erstelle jetzt Snapshot...")
                        break
            
            # 2. Während der MJPEG Stream noch offen ist, fordern wir das Einzelbild an
            frame_r = requests.get(frame_url, timeout=10)
            if frame_r.status_code == 200 and len(frame_r.content) > 1000:
                with open(output_path, "wb") as f:
                    f.write(frame_r.content)
                print(f"Erfolg! Snapshot gespeichert unter {output_path} ({len(frame_r.content)} Bytes)")
                return True
            else:
                print(f"Fehler beim Snapshot: Status {frame_r.status_code}, Größe {len(frame_r.content)} Bytes")
                return False
                
    except Exception as e:
        print(f"Fehler in Brio Session: {e}")
        return False

if __name__ == "__main__":
    capture_brio_snapshot()
