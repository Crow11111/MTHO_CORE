# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
MX (Brio): Nur Bilder holen und speichern – kein Analyse-Schritt.
Zweck: Prüfen, ob überhaupt echte Aufnahmen ankommen (du kannst die Ordner durchsehen).
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from src.network.go2rtc_client import get_snapshot, is_configured

# Speicherort: data/mx_test/ (nur MX-Aufnahmen zum manuellen Prüfen)
SAVE_DIR = Path(os.getenv("MX_SAVE_DIR", str(PROJECT_ROOT / "data" / "mx_test")))
NUM_IMAGES = int(os.getenv("MX_SAVE_NUM", "5"))


def main():
    if not is_configured():
        print("Kamera nicht konfiguriert (GO2RTC_* oder CAMERA_SNAPSHOT_URL).")
        return 1
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Speichere {NUM_IMAGES} MX-Bilder nach {SAVE_DIR}")
    for i in range(NUM_IMAGES):
        ok, data, _ = get_snapshot(timeout=15.0)
        if not ok or not isinstance(data, bytes):
            print(f"  [{i+1}] Fehler: {data}")
            continue
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = SAVE_DIR / f"mx_{ts}_{i+1}.jpg"
        path.write_bytes(data)
        print(f"  [{i+1}] {path} ({len(data)} bytes)")
    print("Fertig. Bilder im Ordner prüfen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
