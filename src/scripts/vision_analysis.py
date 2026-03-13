# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE: Vision Analysis
Takes a snapshot and sends it to OC Brain for description/analysis.
"""
import base64
import os
import sys
from loguru import logger
from src.network.go2rtc_client import get_snapshot
from src.network.openclaw_client import send_event_to_oc_brain

def analyze_vision(stream_name: str = None, prefer_scout_mx: bool = True):
    from src.network.go2rtc_client import SCOUT_MX_SNAPSHOT_URL
    logger.info("Starte Vision-Analyse...")
    prefer = "scout_mx" if (prefer_scout_mx and SCOUT_MX_SNAPSHOT_URL) else None
    ok, data, snapshot_source = get_snapshot(stream_name, prefer_source=prefer)
    if not ok:
        logger.error("Snapshot fehlgeschlagen (Quelle {}): {}", snapshot_source or "?", data)
        return False

    b64_img = base64.b64encode(data).decode("utf-8")
    event = {
        "source": "dreadnought",
        "node_id": "pc-vision",
        "event_type": "vision_analysis",
        "data": {
            "snapshot_b64": b64_img,
            "snapshot_source": snapshot_source or "unknown",
            "prompt": "Beschreibe was du auf diesem Bild siehst. Achte auf Personen oder auffällige Veränderungen."
        }
    }
    
    logger.info("Sende Bild an OC Brain ({} bytes)...", len(b64_img))
    success, response = send_event_to_oc_brain(event)
    
    if success:
        logger.success("Brain Antwort: {}", response)
        return response
    else:
        logger.error("Brain Fehler: {}", response)
        return None

if __name__ == "__main__":
    analyze_vision()
