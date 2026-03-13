import subprocess
import time
import os

ffmpeg_path = r"C:\CORE\driver\go2rtc_win64\ffmpeg.exe"
log_path = r"C:\CORE\driver\go2rtc_win64\brio_streamer.log"

command = [
    ffmpeg_path,
    "-f", "dshow",
    "-rtbufsize", "1000M",
    "-vcodec", "mjpeg",
    "-i", 'video=Logitech BRIO',
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "mpegts",
    "udp://127.0.0.1:12345"
]

print(f"Starte Brio-Streamer mit Log: {log_path}")

with open(log_path, "w") as log_file:
    process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)
    print(f"FFmpeg gestartet mit PID {process.pid}")

time.sleep(10)
if process.poll() is None:
    print("Streamer läuft seit 10 Sekunden.")
else:
    print(f"Streamer beendet mit Code {process.returncode}. Prüfe Logs!")
