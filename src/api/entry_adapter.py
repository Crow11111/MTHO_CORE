# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
GQA F13 - Entry Adapter.
Normalisiert heterogene Webhook-Payloads zu NormalizedEntry für Downstream (Gravitator, Triage).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel


class NormalizedEntry(BaseModel):
    source: str       # "whatsapp" | "ha" | "oc" | "api"
    payload: dict     # flach, kein Session-Ref
    timestamp: str    # ISO8601
    auth_ctx: dict    # optional: {method, client_id}


VALID_SOURCES = frozenset({"whatsapp", "ha", "oc", "api"})


def _ensure_dict(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    return {"raw": raw}


def _normalize_ha(raw: dict) -> dict:
    """HA: action/message, inject_text, forwarded_text, assist."""
    out: dict[str, Any] = {}
    if "action" in raw:
        out["action"] = raw.get("action", "text_input")
    if "message" in raw:
        out["text"] = raw.get("message") or ""
    elif "text" in raw:
        out["text"] = raw.get("text", "")
    if "user_id" in raw:
        out["user_id"] = raw.get("user_id")
    if "data" in raw and isinstance(raw["data"], dict):
        out.update({k: v for k, v in raw["data"].items() if not isinstance(v, (dict, list)) or v is None})
    if "context" in raw:
        out["context"] = raw.get("context")
    if "text" not in out:
        out["text"] = raw.get("message") or raw.get("text") or ""
    return out


def _normalize_whatsapp(raw: dict) -> dict:
    """WhatsApp: nested message.conversation, extendedTextMessage.text."""
    msg = raw.get("message") or {}
    if not isinstance(msg, dict):
        msg = {}
    text = (
        msg.get("conversation")
        or (msg.get("extendedTextMessage") or {}).get("text")
        or raw.get("body")
        or raw.get("text")
        or ""
    )
    if isinstance(text, str):
        text = text.strip()
    else:
        text = str(text)
    sender = (
        (raw.get("key") or {}).get("remoteJid")
        or raw.get("sender")
        or raw.get("from", "unknown")
    )
    audio_msg = msg.get("audioMessage") or msg.get("pttMessage")
    return {
        "text": text,
        "sender": sender,
        "has_audio": bool(audio_msg),
        "audio_seconds": (audio_msg or {}).get("seconds") if isinstance(audio_msg, dict) else None,
    }


def _normalize_oc(raw: dict) -> dict:
    """OC: rat_submission oder ähnliche Struktur."""
    p = raw.get("payload") or raw
    if not isinstance(p, dict):
        p = {}
    return {
        "topic": p.get("topic"),
        "body": p.get("body"),
        "from": p.get("from") or raw.get("from"),
        "type": p.get("type") or raw.get("type"),
    }


def _normalize_api(raw: dict) -> dict:
    """API: direkt flach übernehmen."""
    return {k: v for k, v in raw.items() if not callable(v) and not hasattr(v, "__dict__")}


def normalize_request(
    source: str,
    raw_payload: Any,
    auth_ctx: dict | None = None,
) -> NormalizedEntry:
    """
    Normalisiert rohen Webhook-Payload zu NormalizedEntry.

    Args:
        source: "whatsapp" | "ha" | "oc" | "api"
        raw_payload: Roher Request-Body
        auth_ctx: Optional {method, client_id}

    Returns:
        NormalizedEntry mit flachem payload, ISO8601 timestamp
    """
    if source not in VALID_SOURCES:
        raise ValueError(f"Invalid source: {source}. Must be one of {sorted(VALID_SOURCES)}")
    raw = _ensure_dict(raw_payload)
    norm = {
        "ha": _normalize_ha,
        "whatsapp": _normalize_whatsapp,
        "oc": _normalize_oc,
        "api": _normalize_api,
    }[source](raw)
    return NormalizedEntry(
        source=source,
        payload=norm,
        timestamp=datetime.now(timezone.utc).isoformat(),
        auth_ctx=dict(auth_ctx) if auth_ctx else {},
    )
