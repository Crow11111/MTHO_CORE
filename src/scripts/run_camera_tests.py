# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Wrapper: Führt MX-, Brio-Szenario- und Tapo-Tests sequenziell aus.
Erfolgskriterien: MX mind. 1 .jpg in data/mx_test/, Brio mind. 1 Eintrag in protocol.jsonl, Tapo mind. 1 .jpg in data/tapo_garden/.
Voraussetzung für MX: go2rtc (localhost:1984, Stream „pc“) ODER camera_snapshot_server.py laufend + CAMERA_SNAPSHOT_URL.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# (Modulname, zusätzliche CLI-Argumente)
TESTS = [
    ("src.scripts.mx_save_images_only", []),
    ("src.scripts.brio_scenario_periodic", ["once"]),
    ("src.scripts.tapo_garden_recognize", []),
]


def main():
    for mod, extra in TESTS:
        cmd = [sys.executable, "-m", mod] + extra
        print(f"Running: {' '.join(cmd)}")
        r = subprocess.run(cmd, cwd=PROJECT_ROOT)
        if r.returncode != 0:
            print(f"FEHLER bei {mod} (Exit {r.returncode})")
            return 1
    print("Alle Kamera-Tests erfolgreich ausgeführt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
