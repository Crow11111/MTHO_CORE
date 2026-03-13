# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Go2RTC-Client für CORE.

Architektur: Scout (Raspi/HA) hält die MX Brio per USB und liefert den Stream
via go2rtc (Port 1984 / RTSP 8554). Der PC (Dreadnought) konsumiert Snapshots
on demand und führt Vision-Analyse lokal aus.

Kaskade: go2rtc (Scout) → Scout-MX (HA camera_proxy) → Tapo/Fallback.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

GO2RTC_BASE_URL = os.getenv("GO2RTC_BASE_URL", "http://192.168.178.54:1984").rstrip("/")
GO2RTC_STREAM_NAME = os.getenv("GO2RTC_STREAM_NAME", "mx_brio")
SCOUT_MX_SNAPSHOT_URL = os.getenv("SCOUT_MX_SNAPSHOT_URL", "").strip()
CAMERA_SNAPSHOT_URL = os.getenv("CAMERA_SNAPSHOT_URL", "").strip()
_HASS_TOKEN = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()


def snapshot_url(stream_name: str = None) -> str:
    """URL für ein JPEG-Snapshot. Wenn CAMERA_SNAPSHOT_URL gesetzt: Fallback; sonst go2rtc."""
    # Erster Versuch: go2rtc (lokal)
    name = stream_name or GO2RTC_STREAM_NAME
    return f"{GO2RTC_BASE_URL}/api/frame.jpeg?src={name}"


def get_snapshot(
    stream_name: str = None,
    timeout: float = 10.0,
    prefer_source: str | None = None,
) -> tuple[bool, bytes | str, str]:
    """
    Holt ein JPEG-Snapshot vom Scout (go2rtc) oder HA.

    prefer_source=="scout_mx": NUR Scout-MX (HA camera_proxy); kein Fallback.
    prefer_source is None: Kaskade go2rtc (Scout direkt) → Scout-MX (HA proxy) → Fallback.
    Returns: (success, jpeg_bytes|Fehlermeldung, quell_label)
    """
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _fetch(url: str, headers: dict = None) -> tuple[bool, bytes | str]:
        try:
            r = requests.get(url or "", timeout=timeout, verify=False, headers=headers or {})
            r.raise_for_status()
            data = r.content
            if data and len(data) >= 100 and data[:2] == b"\xff\xd8":
                return True, data
            return False, "Antwort ist kein gültiges JPEG"
        except Exception as e:
            return False, str(e)

    def _ha_headers() -> dict:
        if _HASS_TOKEN:
            return {"Authorization": f"Bearer {_HASS_TOKEN}"}
        return {}

    if prefer_source == "scout_mx":
        if not SCOUT_MX_SNAPSHOT_URL:
            return False, "SCOUT_MX_SNAPSHOT_URL nicht gesetzt", "scout_mx"
        ok, out = _fetch(SCOUT_MX_SNAPSHOT_URL, _ha_headers())
        if ok:
            return True, out, "scout_mx"
        return False, f"Scout-MX nicht erreichbar: {out}", "scout_mx"

    # Kaskade: go2rtc direkt (Scout, schnellster Weg) → HA camera_proxy → Fallback
    name = stream_name or GO2RTC_STREAM_NAME
    url = f"{GO2RTC_BASE_URL}/api/frame.jpeg?src={name}"
    ok, out = _fetch(url)
    if ok:
        return True, out, "go2rtc"

    if SCOUT_MX_SNAPSHOT_URL:
        ok, out = _fetch(SCOUT_MX_SNAPSHOT_URL, _ha_headers())
        if ok:
            return True, out, "scout_mx"

    if CAMERA_SNAPSHOT_URL:
        ok, out = _fetch(CAMERA_SNAPSHOT_URL, _ha_headers())
        if ok:
            return True, out, "camera_snapshot"
        return False, f"Fallback failed: {out}", "camera_snapshot"

    return False, "Keine Snapshot-Quelle erreichbar (go2rtc / Scout-MX / Fallback)", ""


def is_configured() -> bool:
    """True, wenn eine Snapshot-Quelle konfiguriert ist."""
    return (
        bool(GO2RTC_BASE_URL and GO2RTC_STREAM_NAME)
        or bool(SCOUT_MX_SNAPSHOT_URL)
        or bool(CAMERA_SNAPSHOT_URL)
    )


def streams_api_url() -> str:
    """URL der go2rtc API-Streams-Liste (z. B. für Auflistung verfügbarer Streams)."""
    return f"{GO2RTC_BASE_URL}/api/streams"
