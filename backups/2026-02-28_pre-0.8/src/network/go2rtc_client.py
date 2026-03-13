"""
Go2RTC-Client für ATLAS_CORE (Kamera am PC).
Läuft unter Windows aus driver/go2rtc_win64/; Standard-UI/API: http://localhost:1984.
Liest GO2RTC_BASE_URL und GO2RTC_STREAM_NAME aus .env.
Schnittstelle: Snapshot (Einzelbild) für Tests/Dashboard; Stream-URLs für HA/WebRTC.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

GO2RTC_BASE_URL = os.getenv("GO2RTC_BASE_URL", "http://localhost:1984").rstrip("/")
GO2RTC_STREAM_NAME = os.getenv("GO2RTC_STREAM_NAME", "pc")
# Optional: On-Demand-Snapshot (z.B. camera_snapshot_server.py) – Webcam nur bei Abruf aktiv
CAMERA_SNAPSHOT_URL = os.getenv("CAMERA_SNAPSHOT_URL", "").strip()


def snapshot_url(stream_name: str = None) -> str:
    """URL für ein JPEG-Snapshot. Wenn CAMERA_SNAPSHOT_URL gesetzt: Fallback; sonst go2rtc."""
    # Erster Versuch: go2rtc (lokal)
    name = stream_name or GO2RTC_STREAM_NAME
    return f"{GO2RTC_BASE_URL}/api/frame.jpeg?src={name}"


def get_snapshot(stream_name: str = None, timeout: float = 10.0) -> tuple[bool, bytes | str]:
    """
    Holt ein JPEG-Snapshot: Versucht go2rtc, bei Fehler Fallback auf CAMERA_SNAPSHOT_URL.
    Returns: (success, jpeg_bytes oder Fehlermeldung)
    """
    import requests
    import urllib3
    # SSL-Warnungen unterdrücken für lokale IP-Kameras
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 1. Versuch: go2rtc
    url = snapshot_url(stream_name)
    try:
        r = requests.get(url, timeout=timeout, verify=False)
        r.raise_for_status()
        data = r.content
        if data and len(data) >= 100 and data[:2] == b"\xff\xd8":
            return True, data
    except Exception as e:
        # Nur loggen/ignorieren wenn Fallback verfügbar
        if not CAMERA_SNAPSHOT_URL:
            return False, f"go2rtc failed: {str(e)}"

    # 2. Versuch: Fallback auf CAMERA_SNAPSHOT_URL
    if CAMERA_SNAPSHOT_URL:
        try:
            headers = {}
            if "api/camera_proxy" in CAMERA_SNAPSHOT_URL:
                # Token aus .env (HASS_TOKEN) nutzen
                token = os.getenv("HASS_TOKEN")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            
            r = requests.get(CAMERA_SNAPSHOT_URL, timeout=timeout, verify=False, headers=headers)
            r.raise_for_status()
            data = r.content
            if data and len(data) >= 100 and data[:2] == b"\xff\xd8":
                return True, data
            return False, "Fallback-Antwort ist kein gültiges JPEG"
        except Exception as e:
            return False, f"Fallback failed: {str(e)}"
    
    return False, "Keine funktionierende Snapshot-Quelle gefunden"


def is_configured() -> bool:
    """True, wenn eine Snapshot-Quelle konfiguriert ist (go2rtc oder CAMERA_SNAPSHOT_URL)."""
    return bool(CAMERA_SNAPSHOT_URL) or bool(GO2RTC_BASE_URL and GO2RTC_STREAM_NAME)


def streams_api_url() -> str:
    """URL der go2rtc API-Streams-Liste (z. B. für Auflistung verfügbarer Streams)."""
    return f"{GO2RTC_BASE_URL}/api/streams"
