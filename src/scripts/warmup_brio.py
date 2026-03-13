# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import requests
import time
import sys

def maintain_stream(stream_name="pc", base_url="http://localhost:1984"):
    url = f"{base_url}/api/streams?src={stream_name}"
    print(f"Versuche Stream '{stream_name}' aktiv zu halten...")
    
    try:
        # Wir fordern den Stream an, um go2rtc zu signalisieren, dass er aktiv sein soll.
        # go2rtc 'exec' Quellen werden oft erst bei Bedarf gestartet.
        with requests.get(f"{base_url}/api/frame.jpeg?src={stream_name}", stream=True, timeout=10) as r:
            if r.status_code == 200:
                print("Kamera geweckt. Halte Verbindung für 10 Sekunden offen...")
                time.sleep(10)
                print("Warm-up beendet.")
            else:
                print(f"Fehler beim Wecken: {r.status_code}")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    maintain_stream()
