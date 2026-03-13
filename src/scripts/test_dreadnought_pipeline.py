# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test an Dreadnought: Pipeline-Check (OC Brain, Event-Ingest, Voice-Roles).
Läuft auf Dreadnought; Orchestrator führt aus zur Verifikation.
"""
from __future__ import annotations

import json
import sys
import urllib.request

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def main():
    out = []
    # 1) OC Brain: Event senden, Antwort prüfen
    try:
        from src.network.openclaw_client import send_event_to_oc_brain, is_configured
        if is_configured():
            ok, msg = send_event_to_oc_brain(
                {"source": "dreadnought", "node_id": "test-pipeline", "event_type": "orchestrator_test", "data": {}},
                timeout=30,
            )
            out.append(("OC Brain", "OK" if ok else "FAIL", msg[:200] if msg else ""))
        else:
            out.append(("OC Brain", "SKIP", "nicht konfiguriert"))
    except Exception as e:
        out.append(("OC Brain", "FAIL", str(e)[:150]))

    # 2) Lokale API: /api/core/voice/roles (kein Key nötig)
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:8000/api/core/voice/roles",
            method="GET",
        ), timeout=3)
        d = json.loads(r.read().decode())
        roles = d.get("roles", [])
        out.append(("Voice/roles", "OK" if roles else "FAIL", str(len(roles)) + " Rollen"))
    except Exception as e:
        out.append(("Voice/roles", "SKIP" if "refused" in str(e).lower() or "10061" in str(e) else "FAIL", str(e)[:80]))

    # 3) Event-Ingest (API muss laufen)
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:8000/api/core/event",
            data=json.dumps({"source": "test", "node_id": "dreadnought", "event_type": "pipeline_test", "data": {}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        ), timeout=3)
        d = json.loads(r.read().decode())
        out.append(("Event-Ingest", "OK" if d.get("ok") and d.get("id") else "FAIL", d.get("id", "")))
    except Exception as e:
        out.append(("Event-Ingest", "SKIP" if "refused" in str(e).lower() or "10061" in str(e) else "FAIL", str(e)[:80]))

    for name, status, detail in out:
        print(f"{name}: {status} {detail}")
    fails = [o for o in out if o[1] == "FAIL"]
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
