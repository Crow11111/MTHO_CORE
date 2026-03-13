# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Scout-MX einrichten und prüfen: HA /api/states → camera.* filtern → Entity wählen →
set_scout_mx_snapshot_url aufrufen → optional Proof + Report „Sehen“.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Plausible Scout-MX entity_id / friendly_name Muster (Reihenfolge = Priorität)
SCOUT_MX_PRIO = [
    "camera.scout_mx",
    "camera.mx",
    "camera.usb_scout",
    "camera.local_mx",
]
SCOUT_MX_KEYWORDS = ("scout", "mx")


def _get_ha_states():
    base = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "").strip().rstrip("/")
    token = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()
    if not base or not token:
        return None, "HASS_URL und HASS_TOKEN in .env setzen."
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        import requests
        r = requests.get(
            f"{base}/api/states",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
            timeout=15,
        )
        if r.status_code != 200:
            return None, f"HA API HTTP {r.status_code}"
        return r.json(), None
    except Exception as e:
        return None, str(e)


def _camera_entities(states):
    out = []
    for s in (states or []):
        eid = (s.get("entity_id") or "").strip()
        if not eid.startswith("camera."):
            continue
        attrs = s.get("attributes") or {}
        fn = (attrs.get("friendly_name") or "").strip()
        out.append({"entity_id": eid, "state": s.get("state"), "friendly_name": fn or None})
    return out


def _is_plausible_scout_mx(ent):
    eid = (ent["entity_id"] or "").lower()
    fn = ((ent.get("friendly_name") or "") or "").lower()
    text = f"{eid} {fn}"
    if eid in SCOUT_MX_PRIO or any(eid == p for p in SCOUT_MX_PRIO):
        return True
    if any(k in text for k in SCOUT_MX_KEYWORDS):
        return True
    return False


def _score_entity(ent):
    eid = (ent["entity_id"] or "").lower()
    fn = ((ent.get("friendly_name") or "") or "").lower()
    text = f"{eid} {fn}"
    if eid in SCOUT_MX_PRIO:
        return (0, SCOUT_MX_PRIO.index(eid), text)
    for i, p in enumerate(SCOUT_MX_PRIO):
        if p in eid:
            return (0, i, text)
    if any(k in text for k in SCOUT_MX_KEYWORDS):
        return (1, 0, text)
    return (2, 0, text)


def _pick_scout_mx(cameras):
    candidates = [c for c in cameras if _is_plausible_scout_mx(c)]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]["entity_id"]
    scored = [(e, _score_entity(e)) for e in candidates]
    scored.sort(key=lambda x: (x[1][0], x[1][1], x[1][2]))
    return scored[0][0]["entity_id"]


def main():
    states, err = _get_ha_states()
    if err:
        print(f"Keine Kamera-Entity gefunden – bitte in HA anlegen (FFmpeg/Generic Camera, entity_id z.B. camera.scout_mx). HA: {err}")
        sys.exit(1)

    cameras = _camera_entities(states)
    for c in cameras:
        fn = c.get("friendly_name") or ""
        print(f"  {c['entity_id']} | state={c['state']} | friendly_name={fn}")

    if not cameras:
        print("Keine Kamera-Entity gefunden – bitte in HA anlegen (FFmpeg/Generic Camera, entity_id z.B. camera.scout_mx)")
        sys.exit(1)

    entity_id = _pick_scout_mx(cameras)
    if not entity_id:
        print("Keine Kamera-Entity gefunden – bitte in HA anlegen (FFmpeg/Generic Camera, entity_id z.B. camera.scout_mx)")
        sys.exit(1)
    # set_scout_mx_snapshot_url.py --entity <id> (ohne --dry-run)
    script = PROJECT_ROOT / "src" / "scripts" / "set_scout_mx_snapshot_url.py"
    r = subprocess.run(
        [sys.executable, str(script), "--entity", entity_id],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    env_written = r.returncode == 0 and ".env aktualisiert" in (r.stdout or "") + (r.stderr or "")

    proof_code = None
    report_sehen = None
    proof_script = PROJECT_ROOT / "src" / "scripts" / "proof_hoert_sieht_spricht.py"
    if proof_script.exists():
        rp = subprocess.run(
            [sys.executable, str(proof_script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        proof_code = rp.returncode
        report_path = PROJECT_ROOT / "data" / "proof_hoert_sieht_spricht_report.txt"
        if report_path.exists():
            lines = report_path.read_text(encoding="utf-8", errors="replace").splitlines()
            in_sehen = False
            for line in lines:
                if "[Sehen]" in line:
                    in_sehen = True
                    continue
                if in_sehen:
                    s = line.strip()
                    if s.startswith("OK:") or s.startswith("FAIL:"):
                        report_sehen = s
                        break
                    if s.startswith("["):
                        break

    print("\n--- Ergebnis ---")
    print(f"entity_id: {entity_id}")
    print(f".env geschrieben: {env_written}")
    print(f"Proof Exit: {proof_code}")
    if report_sehen:
        print(f"Sehen: {report_sehen}")
    sys.exit(0 if entity_id and env_written else 1)


if __name__ == "__main__":
    main()
