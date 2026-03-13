import requests
import time
import subprocess
import os

def run():
    print("Bereite go2rtc vor...")
    subprocess.run(["taskkill", "/F", "/IM", "go2rtc.exe"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "ffmpeg.exe"], capture_output=True)
    time.sleep(2)
    
    # Start go2rtc
    go2rtc_path = r"C:\CORE\driver\go2rtc_win64\go2rtc.exe"
    config_path = r"C:\CORE\driver\go2rtc_win64\go2rtc.yaml"
    
    print(f"Starte go2rtc: {go2rtc_path}")
    subprocess.Popen([go2rtc_path, "-config", config_path],
                     cwd=r"C:\CORE\driver\go2rtc_win64",
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    stream_url = "http://localhost:1984/api/stream.mjpeg?src=pc"
    print(f"Verbinde zu MJPEG Stream: {stream_url}")
    
    try:
        # Wir fordern den Stream an und halten ihn offen
        with requests.get(stream_url, stream=True, timeout=25) as r:
            print("Warte auf Kamera-Daten (Initialisierung)...")
            start_time = time.time()
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    print(f"Daten empfangen! ({len(chunk)} Bytes). Kamera aktiv.")
                    # Jetzt den Snapshot anfordern
                    time.sleep(1) # Kurze Pause für Stabilisierung
                    snap_r = requests.get("http://localhost:1984/api/frame.jpeg?src=pc", timeout=5)
                    if len(snap_r.content) > 1000:
                        with open("final_brio_snap.jpg", "wb") as f:
                            f.write(snap_r.content)
                        print(f"ERFOLG! Snapshot gespeichert: final_brio_snap.jpg ({len(snap_r.content)} Bytes)")
                        return True
                    else:
                        print(f"Snapshot fehlgeschlagen: {len(snap_r.content)} Bytes empfangen.")
                    break
                if time.time() - start_time > 20:
                    print("Timeout: Keine Daten vom Stream empfangen.")
                    break
    except Exception as e:
        print(f"Fehler während der Session: {e}")
    
    return False

if __name__ == "__main__":
    run()
