# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Voice Assistant – Wyoming Integration Verification

Prüft ob Wyoming-Komponenten (Whisper STT, Piper TTS, openWakeWord) und
Assist Pipelines in Home Assistant korrekt integriert sind.

Nutzt: HAClient aus src/connectors/home_assistant.py (Fallback: requests bei SSL-Problemen)
Env: HASS_URL, HASS_TOKEN (oder HA_URL, HA_TOKEN)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

# Wyoming-typische Muster (Entity-ID oder friendly_name)
WHISPER_PATTERNS = ("whisper", "wyoming_whisper", "faster_whisper")
PIPER_PATTERNS = ("piper", "wyoming_piper")
OPENWAKEWORD_PATTERNS = ("openwakeword", "open_wake_word", "wyoming_openwakeword")


def _matches_pattern(entity_id: str, friendly_name: str, patterns: tuple[str, ...]) -> bool:
    text = f"{entity_id} {friendly_name}".lower()
    return any(p in text for p in patterns)


def _filter_entities(states: list | None, domain: str) -> list[dict]:
    if not states:
        return []
    return [s for s in states if (s.get("entity_id") or "").startswith(f"{domain}.")]


def _check_wyoming_status(states: list | None) -> dict:
    """Ermittelt Status von Whisper, Piper, openWakeWord aus /api/states."""
    result = {
        "whisper_stt": {"available": False, "entities": []},
        "piper_tts": {"available": False, "entities": []},
        "openwakeword": {"available": False, "entities": []},
    }
    if not states:
        return result

    stt_entities = _filter_entities(states, "stt")
    tts_entities = _filter_entities(states, "tts")
    ww_entities = _filter_entities(states, "wake_word")

    for s in stt_entities:
        eid = s.get("entity_id", "")
        fn = (s.get("attributes") or {}).get("friendly_name", "")
        if _matches_pattern(eid, fn, WHISPER_PATTERNS):
            result["whisper_stt"]["entities"].append(
                {"entity_id": eid, "state": s.get("state"), "friendly_name": fn}
            )
    result["whisper_stt"]["available"] = len(result["whisper_stt"]["entities"]) > 0

    for s in tts_entities:
        eid = s.get("entity_id", "")
        fn = (s.get("attributes") or {}).get("friendly_name", "")
        if _matches_pattern(eid, fn, PIPER_PATTERNS):
            result["piper_tts"]["entities"].append(
                {"entity_id": eid, "state": s.get("state"), "friendly_name": fn}
            )
    result["piper_tts"]["available"] = len(result["piper_tts"]["entities"]) > 0

    for s in ww_entities:
        eid = s.get("entity_id", "")
        fn = (s.get("attributes") or {}).get("friendly_name", "")
        if _matches_pattern(eid, fn, OPENWAKEWORD_PATTERNS):
            result["openwakeword"]["entities"].append(
                {"entity_id": eid, "state": s.get("state"), "friendly_name": fn}
            )
    result["openwakeword"]["available"] = len(result["openwakeword"]["entities"]) > 0

    return result


def _extract_pipelines_from_registry(registry: list | None) -> list[dict]:
    """Extrahiert pipeline-relevante Einträge aus Entity Registry (falls vorhanden)."""
    if not registry or not isinstance(registry, list):
        return []
    out = []
    for item in registry:
        eid = (item.get("entity_id") or "").strip()
        if any(eid.startswith(d) for d in ("stt.", "tts.", "wake_word.", "assist.")):
            out.append({"entity_id": eid, "name": item.get("name") or item.get("original_name")})
    return out


def _fetch_states_sync() -> list | None:
    """Fallback bei SSL-Problemen: requests mit verify=False."""
    import urllib3
    import requests

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    base = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "").strip().rstrip("/")
    token = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()
    if not base or not token:
        return None
    try:
        r = requests.get(
            f"{base}/api/states",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            verify=False,
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


async def _fetch_states_fallback() -> list | None:
    return await asyncio.to_thread(_fetch_states_sync)


async def run_verification():
    from src.connectors.home_assistant import HomeAssistantClient

    report = {
        "connection": False,
        "wyoming": {},
        "assist_pipelines": [],
        "all_stt": [],
        "all_tts": [],
        "all_wake_word": [],
        "errors": [],
    }

    client = HomeAssistantClient()
    states = None

    # 1. Verbindung + States via Connector
    try:
        report["connection"] = await client.check_connection()
        if report["connection"]:
            states = await client.get_states()
    except Exception as e:
        report["errors"].append(f"Connector: {e}")
        if "SSL" in str(e) or "certificate" in str(e).lower():
            report["errors"].append("Hinweis: HASS_VERIFY_SSL=0 setzen oder Fallback nutzen.")

    # 2. Fallback bei SSL/Verbindungsproblemen oder fehlenden States
    if not states:
        states = await _fetch_states_fallback()
        if states:
            report["connection"] = True
            report["errors"] = [e for e in report["errors"] if "Hinweis" not in e]

    if not report["connection"]:
        report["errors"].append("HA nicht erreichbar")
        return report

    if not states:
        report["errors"].append("GET /api/states lieferte keine Daten")
        return report

    # 3. Wyoming-Status
    report["wyoming"] = _check_wyoming_status(states)

    # 4. Alle Voice-Entities (für Report)
    report["all_stt"] = [
        {"entity_id": s.get("entity_id"), "state": s.get("state"), "friendly_name": (s.get("attributes") or {}).get("friendly_name")}
        for s in _filter_entities(states, "stt")
    ]
    report["all_tts"] = [
        {"entity_id": s.get("entity_id"), "state": s.get("state"), "friendly_name": (s.get("attributes") or {}).get("friendly_name")}
        for s in _filter_entities(states, "tts")
    ]
    report["all_wake_word"] = [
        {"entity_id": s.get("entity_id"), "state": s.get("state"), "friendly_name": (s.get("attributes") or {}).get("friendly_name")}
        for s in _filter_entities(states, "wake_word")
    ]

    # 5. Assist Pipelines – Entity Registry (optional, WebSocket-basiert in HA)
    if report["connection"] and not report.get("errors"):
        try:
            registry = await client._get_request("config/entity_registry/list")
            report["assist_pipelines"] = _extract_pipelines_from_registry(registry)
        except Exception:
            pass

    return report


def print_report(report: dict):
    print("\n" + "=" * 60)
    print("CORE Voice Assistant – Wyoming Integration Status")
    print("=" * 60)

    print("\n[1] Verbindung zu Home Assistant")
    print(f"    {'OK' if report.get('connection') else 'FEHLER'}")

    if report.get("errors"):
        print("\n[!] Fehler")
        for e in report["errors"]:
            print(f"    - {e}")

    wy = report.get("wyoming", {})
    print("\n[2] Wyoming-Komponenten")
    print(f"    Whisper STT:    {'OK' if wy.get('whisper_stt', {}).get('available') else 'NICHT GEFUNDEN'}")
    for e in wy.get("whisper_stt", {}).get("entities", []):
        print(f"      - {e.get('entity_id')} ({e.get('state')})")
    print(f"    Piper TTS:      {'OK' if wy.get('piper_tts', {}).get('available') else 'NICHT GEFUNDEN'}")
    for e in wy.get("piper_tts", {}).get("entities", []):
        print(f"      - {e.get('entity_id')} ({e.get('state')})")
    print(f"    openWakeWord:   {'OK' if wy.get('openwakeword', {}).get('available') else 'NICHT GEFUNDEN'}")
    for e in wy.get("openwakeword", {}).get("entities", []):
        print(f"      - {e.get('entity_id')} ({e.get('state')})")

    print("\n[3] Alle STT-Entities")
    for e in report.get("all_stt", [])[:15]:
        print(f"    - {e.get('entity_id')} | {e.get('friendly_name')} | {e.get('state')}")
    if len(report.get("all_stt", [])) > 15:
        print(f"    ... und {len(report['all_stt']) - 15} weitere")

    print("\n[4] Alle TTS-Entities")
    for e in report.get("all_tts", [])[:15]:
        print(f"    - {e.get('entity_id')} | {e.get('friendly_name')} | {e.get('state')}")
    if len(report.get("all_tts", [])) > 15:
        print(f"    ... und {len(report['all_tts']) - 15} weitere")

    print("\n[5] Alle Wake-Word-Entities")
    for e in report.get("all_wake_word", []):
        print(f"    - {e.get('entity_id')} | {e.get('friendly_name')} | {e.get('state')}")

    print("\n" + "=" * 60)


def main():
    if not os.getenv("HASS_URL") and not os.getenv("HA_URL"):
        print("FEHLER: HASS_URL oder HA_URL in .env setzen.")
        sys.exit(1)
    if not os.getenv("HASS_TOKEN") and not os.getenv("HA_TOKEN"):
        print("FEHLER: HASS_TOKEN oder HA_TOKEN in .env setzen.")
        sys.exit(1)

    report = asyncio.run(run_verification())
    print_report(report)

    # JSON-Report für Maschinen
    out_path = PROJECT_ROOT / "data" / "ha_voice_integration_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nJSON-Report: {out_path}")

    wy = report.get("wyoming", {})
    all_ok = (
        report.get("connection")
        and wy.get("whisper_stt", {}).get("available")
        and wy.get("piper_tts", {}).get("available")
        and wy.get("openwakeword", {}).get("available")
    )
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
