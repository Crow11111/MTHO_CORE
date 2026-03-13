# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Tapo (Balkon): Ein Frame holen, speichern, optional Erkennung (Person, Zustand).
Kamerablick in den Garten (Bereich Mülltonnen, Leute vorbei) – nicht durch Fenster in die Wohnung (Spiegelungen).

Bildquelle: TAPO_FRAME_URL = HTTP-URL, die go2rtc bereitstellt (go2rtc holt den Frame per FFmpeg vom RTSP-Stream
und liefert ihn über die API aus; wir brauchen dann kein eigenes FFmpeg). Oder TAPO_RTSP_URL + FFmpeg direkt.
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Bevorzugt: HTTP-URL, die ein Einzelbild liefert (z.B. go2rtc/hassio_ingress frame.mp4 oder frame.jpeg)
TAPO_FRAME_URL = os.getenv("TAPO_FRAME_URL", "").strip()
# Fallback: RTSP, dann wird FFmpeg genutzt
TAPO_RTSP_URL = os.getenv("TAPO_RTSP_URL", "").strip()
SAVE_DIR = Path(os.getenv("TAPO_SAVE_DIR", str(PROJECT_ROOT / "data" / "tapo_garden")))
RUN_ANALYSIS = os.getenv("TAPO_RUN_ANALYSIS", "1").strip().lower() in ("1", "true", "yes")
# Optional: HA Bearer für hassio_ingress-URLs (z.B. TAPO_FRAME_URL über Home Assistant)
HASS_TOKEN = os.getenv("HASS_TOKEN", "").strip()

# FFmpeg: wie camera_snapshot_server – zuerst driver/go2rtc_win64 (mit cwd für DLLs), sonst PATH
FFMPEG_DIR = PROJECT_ROOT / "driver" / "go2rtc_win64"
FFMPEG_EXE = "ffmpeg.exe"
_FFMPEG_PATH = FFMPEG_DIR / FFMPEG_EXE
FFMPEG_PATH = str(_FFMPEG_PATH) if _FFMPEG_PATH.is_file() else os.getenv("FFMPEG_PATH", "ffmpeg")
FFMPEG_CWD = str(FFMPEG_DIR) if _FFMPEG_PATH.is_file() else None


def grab_frame_http(url: str, timeout_sec: int = 15) -> tuple[bool, bytes | str]:
    """Einzelbild per HTTP GET (z.B. https://home:8123/.../api/frame.mp4?src=rtsp://...)."""
    try:
        import requests
        headers = {}
        if HASS_TOKEN and ("8123" in url or "hassio_ingress" in url):
            headers["Authorization"] = f"Bearer {HASS_TOKEN}"
        r = requests.get(url, timeout=timeout_sec, verify=False, headers=headers or None)
        r.raise_for_status()
        data = r.content
        if not data or len(data) < 100:
            return False, "Leere oder zu kleine Antwort"
        # JPEG
        if data[:2] == b"\xff\xd8":
            return True, data
        # MP4 (ftyp bei Offset 4): ein Frame daraus extrahieren
        if len(data) >= 8 and data[4:8] == b"ftyp":
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(data)
                tmp = f.name
            try:
                out = subprocess.run(
                    [FFMPEG_PATH, "-y", "-i", tmp, "-vframes", "1", "-f", "image2", "-c:v", "mjpeg", "pipe:1"],
                    capture_output=True, timeout=10, cwd=FFMPEG_CWD,
                )
                if out.returncode == 0 and out.stdout and out.stdout[:2] == b"\xff\xd8":
                    return True, out.stdout
                return False, "FFmpeg konnte keinen Frame aus MP4 lesen"
            finally:
                os.unlink(tmp)
        return False, "Weder JPEG noch MP4 erkannt"
    except Exception as e:
        return False, str(e)


def grab_frame_rtsp(rtsp_url: str, timeout_sec: int = 15) -> tuple[bool, bytes | str]:
    """Einzelbild von RTSP mit FFmpeg (TCP). Nutzt Projekt-FFmpeg aus driver/go2rtc_win64 inkl. cwd für DLLs."""
    cmd = [
        FFMPEG_PATH, "-y",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-vframes", "1",
        "-f", "image2", "-c:v", "mjpeg",
        "pipe:1",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=timeout_sec, cwd=FFMPEG_CWD or str(PROJECT_ROOT))
        if out.returncode != 0:
            err = (out.stderr or b"").decode("utf-8", errors="replace").strip()
            return False, err or f"ffmpeg exit {out.returncode}"
        if not out.stdout or len(out.stdout) < 100:
            err = (out.stderr or b"").decode("utf-8", errors="replace").strip()
            return False, err or "ffmpeg lieferte keine Bilddaten"
        data = out.stdout
        if not data or len(data) < 100 or data[:2] != b"\xff\xd8":
            return False, "Kein gültiges JPEG von FFmpeg"
        return True, data
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except FileNotFoundError:
        return False, f"FFmpeg nicht gefunden: {FFMPEG_PATH}"
    except Exception as e:
        return False, str(e)


def main():
    if not TAPO_FRAME_URL and not TAPO_RTSP_URL:
        print("TAPO_FRAME_URL oder TAPO_RTSP_URL in .env setzen.")
        print("  TAPO_FRAME_URL = HTTP-URL, die ein Einzelbild liefert (z.B. hassio_ingress/.../api/frame.mp4?src=rtsp://home:8554/Balkon_HD?mp4)")
        print("  TAPO_RTSP_URL  = rtsp://home:8554/Balkon_HD (Fallback mit FFmpeg)")
        return 1
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = SAVE_DIR / f"tapo_garden_{ts}.jpg"

    ok, out = False, ""
    if TAPO_FRAME_URL:
        ok, out = grab_frame_http(TAPO_FRAME_URL)
        if not ok and TAPO_RTSP_URL and "401" in str(out):
            print("TAPO_FRAME_URL 401 (z. B. Ingress) – Fallback auf TAPO_RTSP_URL …")
            ok, out = grab_frame_rtsp(TAPO_RTSP_URL)
    if not ok and TAPO_RTSP_URL:
        ok, out = grab_frame_rtsp(TAPO_RTSP_URL)
    if not ok:
        print(f"Frame fehlgeschlagen: {out}")
        return 1
    path.write_bytes(out)
    print(f"Gespeichert: {path} ({len(out)} bytes)")

    if RUN_ANALYSIS:
        from src.ai.brio_image_analyzer import analyze_and_parse
        result = analyze_and_parse(out)
        print(f"Person: {result.get('person_visible')} | State: {result.get('state')} | Need more: {result.get('need_more')}")
        log_line = f"{ts} | person={result.get('person_visible')} | state={result.get('state')}\n"
        (SAVE_DIR / "recognize.log").open("a", encoding="utf-8").write(log_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
