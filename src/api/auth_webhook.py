"""
Webhook-Auth-Dependencies für ATLAS_CORE API.
Shared-Secret / Bearer / API-Key Checks mit constant-time Vergleich.
"""
from __future__ import annotations

import os
import secrets as secmod
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _constant_time_compare(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return secmod.compare_digest(a.strip(), b.strip())


def verify_whatsapp_auth(x_atlas_webhook_secret: str | None = Header(None, alias="X-ATLAS-WEBHOOK-SECRET")):
    """Shared-Secret Header-Check für WhatsApp-Webhook."""
    expected = os.getenv("ATLAS_WEBHOOK_SECRET", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="ATLAS_WEBHOOK_SECRET nicht konfiguriert")
    if not _constant_time_compare(x_atlas_webhook_secret, expected):
        raise HTTPException(status_code=401, detail="Ungültiger oder fehlender Webhook-Secret")


def verify_ha_auth(authorization: str | None = Header(None)):
    """Bearer-Token-Check für HA-Webhook."""
    expected = os.getenv("HA_WEBHOOK_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="HA_WEBHOOK_TOKEN nicht konfiguriert")
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not _constant_time_compare(token, expected):
        raise HTTPException(status_code=401, detail="Ungültiger oder fehlender Bearer-Token")


def verify_oc_auth(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None),
):
    """API-Key-Check für OC-Channel (X-API-Key oder Bearer)."""
    expected = os.getenv("OPENCLAW_GATEWAY_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="OPENCLAW_GATEWAY_TOKEN nicht konfiguriert")
    token = x_api_key
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not _constant_time_compare(token, expected):
        raise HTTPException(status_code=401, detail="Ungültiger oder fehlender API-Key")
