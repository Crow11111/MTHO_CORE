# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Token-Rotation für CORE (90-Tage-Empfehlung, GQA F1).

Generiert neue sichere Werte für:
- CORE_WEBHOOK_SECRET
- HA_WEBHOOK_TOKEN
- OPENCLAW_GATEWAY_TOKEN (optional)

Aktualisiert .env und schreibt TOKEN_ROTATED_AT.
Manuelle Schritte: HA Webhook-URL Token anpassen, OC Brain Gateway-Token setzen.
"""
from __future__ import annotations

import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

ROTATION_DAYS = 90
ENV_PATH = PROJECT_ROOT / ".env"


def generate_hex_token(length: int = 64) -> str:
    return secrets.token_hex(length // 2)


def main() -> int:
    if not ENV_PATH.is_file():
        print("FEHLER: .env nicht gefunden:", ENV_PATH)
        return 1

    content = ENV_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    updated = []
    replaced = {}

    for line in lines:
        if line.strip().startswith("#"):
            updated.append(line)
            continue
        if "=" not in line:
            updated.append(line)
            continue
        key, _, rest = line.partition("=")
        key = key.strip()
        if key == "CORE_WEBHOOK_SECRET":
            new_val = generate_hex_token(64)
            replaced["CORE_WEBHOOK_SECRET"] = new_val
            updated.append(f'{key}="{new_val}"')
        elif key == "HA_WEBHOOK_TOKEN":
            new_val = generate_hex_token(64)
            replaced["HA_WEBHOOK_TOKEN"] = new_val
            updated.append(f'{key}="{new_val}"')
        elif key == "OPENCLAW_GATEWAY_TOKEN":
            new_val = generate_hex_token(64)
            replaced["OPENCLAW_GATEWAY_TOKEN"] = new_val
            updated.append(f'{key}="{new_val}"')
        elif key == "TOKEN_ROTATED_AT":
            updated.append(f'{key}="{datetime.now(timezone.utc).isoformat()}"')
        else:
            updated.append(line)

    if not replaced:
        print("Keine Token zum Rotieren gefunden (CORE_WEBHOOK_SECRET, HA_WEBHOOK_TOKEN, OPENCLAW_GATEWAY_TOKEN).")
        return 0

    if "TOKEN_ROTATED_AT" not in content:
        updated.append(f'\n# Letzte Token-Rotation (alle {ROTATION_DAYS} Tage ausführen)')
        updated.append(f'TOKEN_ROTATED_AT="{datetime.now(timezone.utc).isoformat()}"')

    ENV_PATH.write_text("\n".join(updated) + "\n", encoding="utf-8")
    print("Token rotiert:", ", ".join(replaced.keys()))
    print("TOKEN_ROTATED_AT gesetzt.")
    print("\nManuelle Schritte:")
    print("1. Home Assistant: HA_WEBHOOK_TOKEN in Automation/rest_command anpassen.")
    print("2. OC Brain (VPS): OPENCLAW_GATEWAY_TOKEN in OpenClaw-Config setzen.")
    print("3. WhatsApp-Webhook: X-CORE-WEBHOOK-SECRET bei HA anpassen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
