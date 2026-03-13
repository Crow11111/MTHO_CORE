# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
On-Demand-Snapshot-Server für eine Webcam (z.B. Logitech Brio) unter Windows.
Die Kamera wird nur bei jedem HTTP-GET aktiviert (ein Frame), nicht dauerhaft.
Liest Konfiguration aus .env; FFmpeg muss verfügbar sein (driver/go2rtc_win64 oder PATH).
"""
import os
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Projekt-Root für .env und ffmpeg
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Konfiguration
CAMERA_DEVICE_NAME = os.getenv("CAMERA_DEVICE_NAME", "Logitech BRIO").strip()
CAMERA_SNAPSHOT_PORT = int(os.getenv("CAMERA_SNAPSHOT_PORT", "8555"))
CAMERA_VIDEO_SIZE = os.getenv("CAMERA_VIDEO_SIZE", "1280x720").strip()

# FFmpeg: zuerst im driver-Ordner, sonst PATH
FFMPEG_DIR = PROJECT_ROOT / "driver" / "go2rtc_win64"
FFMPEG_EXE = "ffmpeg.exe"
FFMPEG_PATH = FFMPEG_DIR / FFMPEG_EXE
if not FFMPEG_PATH.is_file():
    FFMPEG_PATH = FFMPEG_EXE


def _capture_with_device(device_name: str) -> tuple[bool, bytes | str]:
    """Ein Einzelbild von der Webcam holen (FFmpeg dshow, -vframes 1)."""
    cmd = [
        str(FFMPEG_PATH),
        "-y",
        "-f", "dshow",
        "-video_size", CAMERA_VIDEO_SIZE,
        "-vframes", "1",
        "-i", f'video="{device_name}"',
        "-f", "image2",
        "-c:v", "mjpeg",
        "pipe:1",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=15,
            cwd=str(FFMPEG_DIR) if (FFMPEG_DIR / FFMPEG_EXE).is_file() else None,
        )
        if result.returncode != 0:
            err = (result.stderr or b"").decode("utf-8", errors="replace").strip()
            return False, err or f"FFmpeg exit code {result.returncode}"
        data = result.stdout
        if not data or len(data) < 100 or data[:2] != b"\xff\xd8":
            return False, "Kein gültiges JPEG von FFmpeg"
        return True, data
    except subprocess.TimeoutExpired:
        return False, "Timeout beim Kamerazugriff"
    except FileNotFoundError:
        return False, f"FFmpeg nicht gefunden: {FFMPEG_PATH}"
    except Exception as e:
        return False, str(e)


def capture_one_frame() -> tuple[bool, bytes | str]:
    """Einzelbild von MX/Brio – versucht CAMERA_DEVICE_NAME, dann Fallback 'Logi Capture' / 'Logitech BRIO'."""
    ok, out = _capture_with_device(CAMERA_DEVICE_NAME)
    if ok:
        return True, out
    # Fallback: Windows zeigt Brio oft als "Logi Capture" (Logitech Capture)
    for fallback in ("Logi Capture", "Logitech BRIO"):
        if fallback == CAMERA_DEVICE_NAME:
            continue
        ok, out = _capture_with_device(fallback)
        if ok:
            return True, out
    return False, out if isinstance(out, str) else "Keine Webcam gefunden"


class SnapshotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/snapshot", "/snapshot.jpg", "/snapshot.jpeg"):
            ok, out = capture_one_frame()
            if ok:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
            else:
                self.send_response(503)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(out.encode("utf-8") if isinstance(out, str) else out)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[Snapshot] {args[0]}")


def main():
    port = CAMERA_SNAPSHOT_PORT
    server = HTTPServer(("0.0.0.0", port), SnapshotHandler)
    print(f"On-Demand-Snapshot-Server: http://localhost:{port}/snapshot.jpg")
    print(f"Kamera: {CAMERA_DEVICE_NAME!r}, Auflösung: {CAMERA_VIDEO_SIZE}")
    print("Strg+C zum Beenden.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
