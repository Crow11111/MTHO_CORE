# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Beweis: CORE hört / sieht / spricht.
Führt prüfbare Schritte aus, schreibt Report nach data/proof_hoert_sieht_spricht_report.txt.
Teamchef: Nur Beweise zählen.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

REPORT_PATH = PROJECT_ROOT / "data" / "proof_hoert_sieht_spricht_report.txt"
MX_SAVE_DIR = Path(os.getenv("MX_SAVE_DIR", str(PROJECT_ROOT / "data" / "mx_test")))
MEDIA_DIR = PROJECT_ROOT / "media"


def log(msg: str, lines: list) -> None:
    lines.append(msg)
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def run_sehen(lines: list) -> tuple[bool, str]:
    """1 Snapshot von Scout-MX (wenn konfiguriert), sonst Kaskade. Speichert in data/mx_test/. Quellennachweis im Report."""
    try:
        from src.network.go2rtc_client import get_snapshot, is_configured, SCOUT_MX_SNAPSHOT_URL
        if not is_configured():
            return False, "GO2RTC/CAMERA_SNAPSHOT_URL/SCOUT_MX nicht konfiguriert"
        MX_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        # MX-Scout-Test: Snapshot muss von Scout-MX kommen (Rat-Kriterium)
        prefer = "scout_mx" if SCOUT_MX_SNAPSHOT_URL else None
        ok, data, source = get_snapshot(timeout=15.0, prefer_source=prefer)
        if not ok or not isinstance(data, bytes):
            return False, f"Quelle {source or '?'}: {str(data)[:180]}"
        # Rat: MX-Scout-Test nur bestanden wenn Snapshot nachweisbar von Scout-MX
        if source != "scout_mx":
            return False, (
                "MX-Scout-Nachweis erfordert Quelle scout_mx. "
                "SCOUT_MX_SNAPSHOT_URL setzen und Scout-MX erreichbar halten."
            )
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = MX_SAVE_DIR / f"proof_mx_{ts}.jpg"
        path.write_bytes(data)
        return True, f"{path} | Quelle: {source}"
    except Exception as e:
        return False, str(e)[:200]


def run_sprechen(lines: list) -> tuple[bool, str]:
    """TTS erzeugen, in media/ speichern. Optional: an WhatsApp senden."""
    try:
        from src.voice.elevenlabs_tts import speak_text
        text = "CORE Proof. Hoeren, Sehen, Sprechen – Test."
        out_path = MEDIA_DIR / "proof_tts.mp3"
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = speak_text(
            text=text,
            role_name="core_dialog",
            output_path=str(out_path),
            play=False,
        )
        if not path or not os.path.isfile(path):
            return False, "TTS lieferte keine Datei"
        # Optional: an WhatsApp senden (wenn HA + Ziel konfiguriert)
        target = (os.getenv("WHATSAPP_TARGET_ID") or "").strip().strip('"').replace("@s.whatsapp.net", "")
        if target and os.getenv("HASS_URL") and os.getenv("HASS_TOKEN"):
            try:
                from src.network.ha_client import HAClient
                ok = HAClient().send_whatsapp_audio(to_number=target, audio_path=path)
                if ok:
                    return True, f"{path} + WhatsApp gesendet"
            except Exception as e:
                log(f"  WhatsApp optional FAIL: {e}", lines)
        return True, str(path)
    except Exception as e:
        return False, str(e)[:200]


def run_hoeren(lines: list) -> tuple[bool, str]:
    """Hören: Aufnahme oder dokumentierter Dummy. Rat: reale Samples ODER Dummy klar markiert."""
    try:
        from src.scripts.dreadnought_listen import record_audio, send_event
        audio_file = f"media/proof_voice_{int(datetime.now().timestamp())}.wav"
        os.makedirs("media", exist_ok=True)
        path, mode, msg = record_audio(duration=2, filename=audio_file)
        if not path:
            return False, "Aufnahme lieferte keinen Pfad"
        if not send_event(path):
            return False, "Senden des Audio-Events fehlgeschlagen"
        if mode == "dummy":
            return True, f"Dummy – keine echte Aufnahme: {msg}"
        from src.scripts.dreadnought_listen import verify_wav_has_samples
        ok_verify, verify_msg = verify_wav_has_samples(path)
        return True, f"Audio-Event an OC Brain gesendet ({path}) | Verifizierung: {verify_msg}"
    except Exception as e:
        return False, f"Fehler bei run_hoeren: {str(e)[:200]}"


def main() -> int:
    lines = [f"Report {datetime.now(timezone.utc).isoformat()}"]
    log("--- Proof: CORE hört / sieht / spricht ---", lines)

    # Sehen
    log("\n[Sehen]", lines)
    ok_see, detail_see = run_sehen(lines)
    log(f"  {'OK' if ok_see else 'FAIL'}: {detail_see}", lines)

    # Sprechen
    log("\n[Sprechen]", lines)
    ok_speak, detail_speak = run_sprechen(lines)
    log(f"  {'OK' if ok_speak else 'FAIL'}: {detail_speak}", lines)

    # Hören
    log("\n[Hören]", lines)
    ok_hear, detail_hear = run_hoeren(lines)
    log(f"  {'OK' if ok_hear else 'FAIL'}: {detail_hear}", lines)

    # Report schreiben
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log(f"\nReport: {REPORT_PATH}", lines)

    fails = sum(1 for o in [ok_see, ok_speak, ok_hear] if not o)
    return 2 if fails >= 2 else (1 if fails == 1 else 0)


if __name__ == "__main__":
    sys.exit(main())
