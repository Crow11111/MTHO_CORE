# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Webhook-Auth-Dependencies für CORE API.
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


def verify_whatsapp_auth(x_core_webhook_secret: str | None = Header(None, alias="X-CORE-WEBHOOK-SECRET")):
    """Shared-Secret Header-Check für WhatsApp-Webhook."""
    expected = os.getenv("CORE_WEBHOOK_SECRET", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="CORE_WEBHOOK_SECRET nicht konfiguriert")
    if not _constant_time_compare(x_core_webhook_secret, expected):
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


def verify_ring0_write(
    x_ring0_token: str | None = Header(None, alias="X-Ring0-Token"),
    authorization: str | None = Header(None),
):
    """Ring-0 Write Gate: Token-Check für Schreibzugriffe auf core_directives/simulation_evidence.
    X-Ring0-Token oder Bearer muss RING0_WRITE_TOKEN entsprechen.
    Wenn RING0_WRITE_TOKEN nicht gesetzt: 503 (Fail-Closed)."""
    expected = os.getenv("RING0_WRITE_TOKEN", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Ring-0 Write Gate: RING0_WRITE_TOKEN nicht konfiguriert (Fail-Closed)",
        )
    token = x_ring0_token
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not _constant_time_compare(token, expected):
        raise HTTPException(
            status_code=403,
            detail="Ring-0 Write Gate: Ungültiger oder fehlender X-Ring0-Token",
        )
