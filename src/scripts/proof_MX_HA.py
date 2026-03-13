# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Beweis-Skript für die MX Brio Integration in Home Assistant.
Prüft Erreichbarkeit der Scout-MX Kamera und validiert das Bild.
"""
import os
import sys
import time
import requests
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Wir brauchen die Vision-Analyse für den "echten" Beweis
sys.path.insert(0, str(PROJECT_ROOT))
from src.ai.brio_image_analyzer import analyze_and_parse

REPORT_PATH = PROJECT_ROOT / "data" / "proof_MX_HA_report.txt"

def main():
    logger.info("Starte proof_MX_HA...")
    
    snapshot_url = os.getenv("SCOUT_MX_SNAPSHOT_URL")
    if not snapshot_url:
        logger.error("SCOUT_MX_SNAPSHOT_URL nicht in .env gefunden!")
        return 1
    
    token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    logger.info(f"Prüfe Snapshot von: {snapshot_url}")
    
    try:
        # 1. Snapshot abrufen
        resp = requests.get(snapshot_url, headers=headers, verify=False, timeout=15)
        if resp.status_code != 200:
            logger.error(f"Snapshot fehlgeschlagen: HTTP {resp.status_code}")
            return 1
        
        image_bytes = resp.content
        logger.info(f"Snapshot empfangen ({len(image_bytes)} Bytes).")
        
        # 2. Bild lokal speichern für Dokumentation
        os.makedirs(PROJECT_ROOT / "data" / "mx_ha_proof", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        img_path = PROJECT_ROOT / "data" / "mx_ha_proof" / f"proof_mx_ha_{timestamp}.jpg"
        img_path.write_bytes(image_bytes)
        logger.info(f"Bild gespeichert: {img_path}")
        
        # 3. Vision-Analyse (Beweis dass es ein echtes Kamerabild ist)
        logger.info("Sende Bild an Gemini Vision zur Verifikation...")
        analysis = analyze_and_parse(image_bytes)
        
        # 4. Report erstellen
        report = f"""CORE MX BRIO HA PROOF REPORT
------------------------------
Zeitstempel: {time.strftime("%Y-%m-%d %H:%M:%S")}
Quelle: {snapshot_url}
Bildpfad: {img_path}

ERGEBNIS:
- Erreichbarkeit: OK (HTTP 200)
- Bildgröße: {len(image_bytes)} Bytes
- Vision-Check:
  - Person sichtbar: {analysis.get('person_visible')}
  - Zustand: {analysis.get('state')}
  - Raw Output: {analysis.get('raw')}

STATUS: {'ERFOLGREICH' if analysis.get('state') else 'TEILWEISE (Bild da, Analyse fehlt)'}
"""
        REPORT_PATH.write_text(report, encoding="utf-8")
        logger.info(f"Report geschrieben nach: {REPORT_PATH}")
        print(report)
        
        return 0
        
    except Exception as e:
        logger.error(f"Fehler beim Proof: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
