# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Setzt SCOUT_MX_SNAPSHOT_URL in .env aus HASS_URL/HA_URL und Entity-ID.
Lädt .env; liest HASS_URL (Fallback HA_URL), HASS_TOKEN (Fallback HA_TOKEN).
Entity-ID: Argument --entity oder Umgebungsvariable SCOUT_MX_ENTITY_ID (Default: camera.scout_mx).
Baut URL = HASS_URL + /api/camera_proxy/<entity_id>; optional GET gegen HA ob Entity existiert.
Schreibt/aktualisiert nur die Zeile SCOUT_MX_SNAPSHOT_URL in .env (keine Löschung anderer Inhalte).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_ENTITY = "camera.scout_mx"


def main() -> None:
    parser = argparse.ArgumentParser(description="SCOUT_MX_SNAPSHOT_URL aus HA-URL und Entity setzen")
    parser.add_argument("--entity", default=os.getenv("SCOUT_MX_ENTITY_ID", DEFAULT_ENTITY),
                        help=f"Camera entity ID (default: {DEFAULT_ENTITY})")
    parser.add_argument("--no-check", action="store_true", help="HA-API-Check überspringen")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, .env nicht schreiben")
    args = parser.parse_args()
    entity_id = (args.entity or DEFAULT_ENTITY).strip()

    base = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "").strip().rstrip("/")
    if not base:
        print("FEHLER: HASS_URL oder HA_URL in .env setzen.")
        sys.exit(1)

    url = f"{base}/api/camera_proxy/{entity_id}"
    token = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()

    if not args.no_check and token:
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            import requests
            r = requests.get(
                f"{base}/api/states/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
                verify=False,
                timeout=10,
            )
            if r.status_code != 200:
                print(f"HINWEIS: Entity {entity_id} in HA nicht gefunden (HTTP {r.status_code}).")
                print("  Kamera in HA anlegen (Generic Camera / FFmpeg) oder --no-check nutzen.")
        except Exception as e:
            print(f"HINWEIS: HA-Check fehlgeschlagen: {e}. Setze URL trotzdem.")

    line = f"SCOUT_MX_SNAPSHOT_URL={url}"
    print(line)
    if args.dry_run:
        print("(Dry-run: .env nicht geändert. Zeile oben ggf. manuell in .env eintragen.)")
        return

    raw = ENV_PATH.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"^(\s*SCOUT_MX_SNAPSHOT_URL\s*=\s*).*$", re.MULTILINE)
    if pattern.search(raw):
        new_raw = pattern.sub(rf"\g<1>{url}", raw)
    else:
        new_raw = raw.rstrip() + "\n\n# Scout-MX (camera_proxy)\n" + line + "\n"
    ENV_PATH.write_text(new_raw, encoding="utf-8")
    print(".env aktualisiert.")


if __name__ == "__main__":
    main()
