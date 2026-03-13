# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import requests
import time
import sys

def keep_alive(stream_name="pc", base_url="http://localhost:1984"):
    url = f"{base_url}/api/stream.mjpeg?src={stream_name}"
    print(f"Halte Stream '{stream_name}' aktiv...")
    while True:
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                print("Verbindung zu go2rtc hergestellt.")
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        print(f"Empfange Daten: {len(chunk)} Bytes", end='\r')
                    else:
                        break
            print("\nVerbindung verloren, neu verbinden...")
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            time.sleep(2)

if __name__ == "__main__":
    keep_alive()
