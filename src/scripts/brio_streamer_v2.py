# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import subprocess
import os
import time

ffmpeg_path = r"C:\CORE\driver\go2rtc_win64\ffmpeg.exe"
log_path = r"C:\CORE\driver\go2rtc_win64\brio_streamer_v2.log"

cmd = [
    ffmpeg_path,
    "-f", "dshow",
    "-rtbufsize", "1000M",
    "-i", 'video=Logitech BRIO',
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "mpegts",
    "udp://127.0.0.1:12345"
]

print(f"Starting FFmpeg to UDP... Logging to {log_path}")
with open(log_path, "w") as f:
    process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
    print(f"Process started with PID: {process.pid}")

# Wait a bit to see if it stays alive
time.sleep(5)
if process.poll() is None:
    print("Process is still running.")
else:
    print(f"Process exited with code: {process.returncode}")
