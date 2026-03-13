# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

from __future__ import annotations

import asyncio
import json
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.auth_webhook import verify_whatsapp_auth
from src.network.ha_client import HAClient
from src.ai.whatsapp_audio_processor import process_whatsapp_audio
from src.ai.llm_interface import core_llm
from src.network.openclaw_client import send_message_to_agent_async, is_configured as oc_configured
from src.api.entry_adapter import normalize_request, NormalizedEntry
from src.logic_core.takt_gate import check_takt_zero

load_dotenv("c:/CORE/.env")


async def _mirror_to_oc_brain(text: str, sender: str, msg_type: str = "whatsapp") -> None:
    """Stufe 1: Fire-and-forget Kopie an OC Brain (non-blocking, bei Fehler nur loggen)."""
    if not oc_configured():
        return
    try:
        payload = f"[{msg_type.upper()}|{sender}] {text}"
        ok, msg = await send_message_to_agent_async(payload, agent_id="main", user=sender, timeout=10.0)
        if ok:
            logger.debug(f"OC Brain Mirror OK: {msg[:80]}")
        else:
            logger.warning(f"OC Brain Mirror fehlgeschlagen: {msg}")
    except Exception as e:
        logger.warning(f"OC Brain Mirror Exception: {e}")

router = APIRouter(prefix="/webhook", tags=["webhooks"])
ha_client = HAClient()

# Sofort-Antwort an HA, damit rest_command (Default-Timeout 10s) nicht abbricht
ACCEPTED_MSG = "[Scout] Nachricht erhalten, verarbeite …"


@router.post("/whatsapp")
async def receive_whatsapp(
    request: Request,
    background_tasks: BackgroundTasks,
    _auth: None = Depends(verify_whatsapp_auth),
):
    """
    Empfängt WhatsApp-Nachrichten über Home Assistant.
    Implementiert Tesseract Topology: Entry Adapter -> Diagonale (Triage) -> Core.
    """
    raw = await request.json()

    # HA rest_command serialisiert den Payload manchmal doppelt (JSON-String statt Dict)
    if isinstance(raw, str):
        try:
            raw_payload = json.loads(raw)
        except json.JSONDecodeError:
            raw_payload = {"raw": raw}
    else:
        raw_payload = raw

    logger.info(f"WhatsApp Webhook Raw: {json.dumps(raw_payload, ensure_ascii=False)[:500]}")

    # 1. Entry Adapter: Normalisierung (Membran)
    try:
        entry: NormalizedEntry = normalize_request("whatsapp", raw_payload)
    except Exception as e:
        logger.error(f"Entry Adapter Normalization Failed: {e}")
        return {"status": "error", "reason": "normalization_failed"}

    # 2. Diagonale Logic (Pre-Routing)
    incoming_text = entry.payload.get("text", "")
    sender = entry.payload.get("sender", "unknown")
    has_audio = entry.payload.get("has_audio", False)
    audio_seconds = entry.payload.get("audio_seconds")

    low = (incoming_text or "").lower()

    # Nur @OC adressiert → für OC, CORE reagiert nicht
    if incoming_text and low.startswith("@oc"):
        logger.info(f"WhatsApp: ignoriert (für @OC): {incoming_text[:80]}...")
        return {"status": "ignored", "reason": "addressed_to_@OC"}

    # Nur bei @Core (am Anfang) reagieren
    if incoming_text and not low.startswith("@core"):
        logger.info(f"WhatsApp: ignoriert (kein @Core-Prefix): {incoming_text[:80]}...")
        return {"status": "ignored", "reason": "no_@Mtho_prefix"}

    # Sprachnachricht: nur bei @Core-Prefix reagieren
    if has_audio and not (incoming_text and low.startswith("@core")):
        logger.info("WhatsApp: Sprachnachricht ignoriert (kein @Core).")
        return {"status": "ignored", "reason": "audio_without_@Core"}

    # ── Sprachnachricht ───────────────────────────────────────────────────────
    message = raw_payload.get("message", {}) if isinstance(raw_payload, dict) else {}
    audio_msg = message.get("audioMessage") or message.get("pttMessage") # raw extraction needed for binary pointers

    if has_audio and audio_msg:
        # [TAKT 0 GATE] - Async check before processing heavy audio logic
        if not await check_takt_zero():
            logger.warning(f"TAKT 0 VETO: System rejected audio request from {sender}")
            return {"status": "veto", "reason": "system_instability_takt0"}

        logger.success(f"🎤 Sprachnachricht von {sender} ({audio_seconds}s)!")

        # Sofort Bestätigung
        ha_client.send_whatsapp(
            to_number=sender,
            text=f"[Scout] 🎤 Sprachmemo ({audio_seconds}s) empfangen. Analysiere..."
        )

        async def run_audio():
            result = await process_whatsapp_audio(audio_msg, sender)
            ha_client.send_whatsapp(to_number=sender, text=f"[CORE] {result}")

        background_tasks.add_task(run_audio)
        asyncio.create_task(_mirror_to_oc_brain(f"[AUDIO {audio_seconds}s]", sender, "whatsapp_voice"))
        return {"status": "audio_processing", "sender": sender, "seconds": audio_seconds}

    # ── Textnachricht ─────────────────────────────────────────────────────────
    if incoming_text:
        # [TAKT 0 GATE] - Async check before LLM Triage
        if not await check_takt_zero():
            logger.warning(f"TAKT 0 VETO: System rejected text request from {sender}")
            return {"status": "veto", "reason": "system_instability_takt0"}

        # @Core-Prefix abziehen
        t = incoming_text.strip()
        if t.lower().startswith("@core"):
            t = t[6:].strip() or t

        logger.success(f"💬 Textnachricht von {sender}: {incoming_text}")

        # 3. Triage / Gravitator Strut (Async)
        # Ring-1 Perf: Triage (sync) in Thread → Event-Loop frei
        triage = await asyncio.to_thread(core_llm.run_triage, t)

        if triage.intent == "command":
            def _cmd():
                domain = triage.target_entity.split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
                service = triage.action or "turn_on"
                success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity or "")
                return f"[Scout] ✅ {service} → {triage.target_entity}" if success else f"[Scout] ❌ Fehler: {service} → {triage.target_entity}"

            reply = await asyncio.to_thread(_cmd)
            ha_client.send_whatsapp(to_number=sender, text=reply)
            asyncio.create_task(_mirror_to_oc_brain(t, sender, "whatsapp_cmd"))
            return {"status": "text_handled", "sender": sender, "intent": triage.intent}

        if triage.intent in ["deep_reasoning", "chat"]:
            # Schwere KI: 202 Accepted
            ha_client.send_whatsapp(to_number=sender, text=ACCEPTED_MSG)

            def run_heavy_and_reply():
                sys_prompt = "Du bist CORE, ein intelligenter Assistent. Antworte präzise und knapp auf WhatsApp."
                reply = core_llm.invoke_heavy_reasoning(sys_prompt, t)
                reply = f"[CORE] {reply}" if reply else "[CORE] (keine Antwort)"
                ha_client.send_whatsapp(to_number=sender, text=reply)

            background_tasks.add_task(run_heavy_and_reply)
            asyncio.create_task(_mirror_to_oc_brain(t, sender, "whatsapp_reasoning"))
            return JSONResponse(
                status_code=202,
                content={"status": "text_queued", "sender": sender, "intent": triage.intent},
            )

        reply = f"[Scout] Nicht verstanden: '{t}'"
        ha_client.send_whatsapp(to_number=sender, text=reply)
        return {"status": "text_handled", "sender": sender, "intent": triage.intent}

    logger.warning(f"Unbekannter Payload Type (Kein Text/Audio). Keys: {list(entry.payload.keys())}")
    return {"status": "unknown", "keys": list(entry.payload.keys())}
