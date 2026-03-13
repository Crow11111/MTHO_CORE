# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Führt die Tests für OC-Kanal und Frontend-Backend-Anbindung aus.

1. test_core_oc_channel (Gateway-Check; optional --send mit -s)
2. test_frontend_backend (API, Chat-History, Restart-Endpoint)

Aufruf:
  python -m src.scripts.run_oc_and_frontend_tests
  python -m src.scripts.run_oc_and_frontend_tests -s   # inkl. Senden einer Testnachricht an OC
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def run(cmd: list[str], name: str) -> bool:
    print(f"\n--- {name} ---")
    r = subprocess.run(cmd, cwd=ROOT)
    ok = r.returncode == 0
    if not ok:
        print(f"  FEHLER: {name} exit code {r.returncode}")
    return ok

def main() -> int:
    send_to_oc = "-s" in sys.argv or "--send" in sys.argv
    args_oc = ["python", "-m", "src.scripts.test_core_oc_channel"]
    if send_to_oc:
        args_oc.append("--send")

    ok1 = run(args_oc, "CORE-OC-Kanal (Gateway" + (" + Testnachricht" if send_to_oc else "") + ")")
    ok2 = run(["python", "-m", "src.scripts.test_frontend_backend"], "Frontend-Backend (API)")

    if not ok1 or not ok2:
        print("\nMindestens ein Test fehlgeschlagen.")
        return 1
    print("\nAlle Tests bestanden.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
