# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Brio-Szenario: In konfigurierbaren Abständen (Standard: 1× pro Minute) ein Bild von der Brio holen,
auswerten (Person sichtbar? Zustand?), protokollieren. Für Laufzeit-Erkennung (Anwesenheit, Auffälligkeiten)
muss das Intervall kurz sein (mind. 1×/Minute); bei Bedarf weitere Snapshots bis die Situation klar ist.
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from loguru import logger

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from src.network.go2rtc_client import get_snapshot, is_configured
from src.ai.brio_image_analyzer import analyze_frame, parse_analysis, PROMPT_MULTI

# Konfiguration (Umgebungsvariablen oder Defaults)
# Laufzeit-Erkennung (Anwesenheit/Notfall) erfordert mind. 1× pro Minute; 50 min nur für ersten Test sinnvoll
INTERVAL_MIN = int(os.getenv("BRIO_SCENARIO_INTERVAL_MIN", "1"))
DURATION_MIN = int(os.getenv("BRIO_SCENARIO_DURATION_MIN", "60"))  # z.B. 1 h = 60 Zyklen bei INTERVAL_MIN=1
MAX_EXTRA_FRAMES = int(os.getenv("BRIO_SCENARIO_MAX_EXTRA", "5"))
LOG_DIR = Path(os.getenv("BRIO_SCENARIO_LOG_DIR", str(PROJECT_ROOT / "data" / "brio_scenario")))
LOG_FILE = LOG_DIR / "protocol.jsonl"


def ensure_log_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def save_image(data: bytes, prefix: str) -> Path:
    ensure_log_dir()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"{prefix}_{ts}.jpg"
    path = LOG_DIR / name
    path.write_bytes(data)
    return path


def run_one_cycle() -> dict:
    """Ein Zyklus: 1 Bild holen → auswerten → ggf. weitere Bilder → final protokollieren."""
    if not is_configured():
        logger.error("Kamera nicht konfiguriert (GO2RTC_* oder CAMERA_SNAPSHOT_URL).")
        return {"ok": False, "error": "camera_not_configured"}

    ok, data, _ = get_snapshot(timeout=15.0)
    if not ok or not isinstance(data, bytes):
        logger.warning(f"Snapshot fehlgeschlagen: {data}")
        return {"ok": False, "error": str(data), "ts": datetime.now(timezone.utc).isoformat()}

    # Erstes Bild speichern und auswerten
    img_path = save_image(data, "brio")
    from src.ai.brio_image_analyzer import analyze_and_parse
    result = analyze_and_parse(data)
    images_used = [str(img_path)]
    need_more = result.get("need_more") and MAX_EXTRA_FRAMES > 0

    # Bei Bedarf weitere Bilder holen und gemeinsam auswerten
    if need_more:
        extra_frames = []
        for i in range(MAX_EXTRA_FRAMES):
            time.sleep(2)
            ok2, data2, _ = get_snapshot(timeout=15.0)
            if ok2 and isinstance(data2, bytes):
                p = save_image(data2, f"brio_extra_{i+1}")
                extra_frames.append(data2)
                images_used.append(str(p))
        if extra_frames:
            # Mehrere Bilder an Gemini: erstes + extras (Gemini kann mehrere Parts)
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                parts = [types.Part.from_bytes(data=d, mime_type="image/jpeg") for d in [data] + extra_frames]
                response = client.models.generate_content(
                    model=os.getenv("BRIO_VISION_MODEL", "gemini-3.1-pro-preview"),
                    contents=[PROMPT_MULTI] + parts,
                )
                if response and response.text:
                    parsed = parse_analysis(response.text)
                    result.update(parsed)
                    result["need_more"] = False
            except Exception as e:
                logger.warning(f"Mehrbild-Auswertung fehlgeschlagen: {e}")

    # Protokoll-Eintrag
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "person_visible": result.get("person_visible"),
        "state": result.get("state", ""),
        "images_used": len(images_used),
        "image_paths": images_used,
        "raw_analysis": result.get("raw", "")[:500],
    }
    ensure_log_dir()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"Brio-Szenario: {entry['state']!r} | Person: {entry['person_visible']} | Bilder: {len(images_used)}")
    return {"ok": True, **entry}


def main():
    """Läuft alle INTERVAL_MIN Minuten für DURATION_MIN Minuten (z.B. nächste Stunde, 2 Zyklen bei 50 min)."""
    logger.add(sys.stderr, level="INFO")
    if not is_configured():
        logger.error("Kamera nicht konfiguriert. GO2RTC_BASE_URL/STREAM oder CAMERA_SNAPSHOT_URL in .env setzen.")
        sys.exit(1)

    interval_sec = INTERVAL_MIN * 60
    duration_sec = DURATION_MIN * 60
    end_time = time.monotonic() + duration_sec
    run = 0

    logger.info(f"Brio-Szenario: alle {INTERVAL_MIN} min, Dauer {DURATION_MIN} min. Log: {LOG_FILE}")

    while time.monotonic() < end_time:
        run += 1
        logger.info(f"--- Zyklus {run} ---")
        run_one_cycle()
        if time.monotonic() >= end_time:
            break
        time.sleep(interval_sec)

    logger.info(f"Brio-Szenario beendet nach {run} Zyklen. Protokoll: {LOG_FILE}")


if __name__ == "__main__":
    # Einmaliger Testlauf: nur ein Zyklus
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        run_one_cycle()
    else:
        main()
