# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test: Snapshot von go2rtc holen (Kamera am PC).
Stellt fest, ob go2rtc läuft und ob ein Bild vom konfigurierten Stream kommt.
Optional: Bild speichern unter data/media/ für Sichtprüfung.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.network.go2rtc_client import (
    GO2RTC_BASE_URL,
    GO2RTC_STREAM_NAME,
    get_snapshot,
    is_configured,
)

def main():
    print("Go2RTC Snapshot-Test")
    print(f"  Base URL: {GO2RTC_BASE_URL}")
    print(f"  Stream:   {GO2RTC_STREAM_NAME}")
    if not is_configured():
        print("  Konfiguration unvollständig (GO2RTC_BASE_URL / GO2RTC_STREAM_NAME).")
        return 1

    ok, result, source = get_snapshot()
    if not ok:
        print(f"  FEHLER (Quelle: {source or '?'}): {result}")
        if "404" in str(result):
            print("  Hinweis: 404 = Stream nicht gefunden. In go2rtc Web-UI (localhost:1984) Stream-Namen prüfen und GO2RTC_STREAM_NAME in .env anpassen.")
        return 1

    # result = bytes (JPEG)
    size = len(result)
    print(f"  OK: JPEG-Bild erhalten, {size} Bytes (Quelle: {source})")
    # Optional: speichern
    media_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "media")
    if not os.path.isabs(media_dir):
        media_dir = os.path.abspath(media_dir)
    os.makedirs(media_dir, exist_ok=True)
    out_path = os.path.join(media_dir, "go2rtc_test_snapshot.jpg")
    with open(out_path, "wb") as f:
        f.write(result)
    print(f"  Gespeichert: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
