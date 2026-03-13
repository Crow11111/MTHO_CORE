# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Prüft, ob das CORE-CORE-Backend für das Dev-Agent-Frontend erreichbar ist.

- GET / (API-Root)
- GET /api/chat/history
- POST /api/services/TestService/restart

Verwendung: Backend muss laufen (z. B. uvicorn). Dann:
  python -m src.scripts.test_frontend_backend

Optional: --base-url http://localhost:8000 (Default)
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import requests

DEFAULT_BASE = os.getenv("CORE_API_URL", "http://localhost:8000")


def main() -> int:
    base = DEFAULT_BASE
    if "--base-url" in sys.argv:
        i = sys.argv.index("--base-url")
        if i + 1 < len(sys.argv):
            base = sys.argv[i + 1].rstrip("/")
    print(f"Prüfe Backend: {base}")
    failed = []

    # 1. API-Root
    try:
        r = requests.get(f"{base}/", timeout=5)
        r.raise_for_status()
        print("  API (GET /): OK")
    except Exception as e:
        print(f"  API (GET /): Fehler – {e}")
        failed.append("API")

    # 2. Chat-History
    try:
        r = requests.get(f"{base}/api/chat/history", timeout=5)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            print("  Chat-History: Antwort keine Liste")
        else:
            print(f"  Chat-History: OK ({len(data)} Einträge)")
    except Exception as e:
        print(f"  Chat-History: Fehler – {e}")
        failed.append("Chat-History")

    # 3. Restart-Endpoint (vom Frontend genutzt)
    try:
        r = requests.post(f"{base}/api/services/TestService/restart", timeout=5)
        r.raise_for_status()
        body = r.json()
        if body.get("success") is not True:
            print("  Restart-Endpoint: Antwort success != true")
        else:
            print("  Restart-Endpoint: OK")
    except Exception as e:
        print(f"  Restart-Endpoint: Fehler – {e}")
        failed.append("Restart")

    if failed:
        print(f"\nFehlgeschlagen: {', '.join(failed)}. Backend starten? (uvicorn src.api.main:app --port 8000)")
        return 1
    print("\nBackend für Frontend bereit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
