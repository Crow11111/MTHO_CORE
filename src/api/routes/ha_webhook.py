# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
GQA Refactor F2 - scout-direct-handler
Steuerbefehle lokal auf Scout; Deep-Reasoning an OC Brain.
SCOUT_DIRECT_MODE=true → ScoutDirectHandler (lokale HA, VPS-Fallback).

Ring-1 Perf: process_text/triage in asyncio.to_thread → Event-Loop nicht blockiert.
[UPDATE 2026-03-06] Integrates Takt 0 Gate and Async I/O.
"""
from __future__ import annotations

import asyncio
import os
from typing import Optional, Dict, Any

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from loguru import logger

from src.api.auth_webhook import verify_ha_auth
from src.api.entry_adapter import normalize_request
from src.network.ha_client import HAClient
from src.ai.llm_interface import mtho_llm
from src.network.openclaw_client import send_message_to_agent_async, is_configured as oc_configured
from src.logic_core.takt_gate import check_takt_zero

async def _mirror_to_oc_brain(text: str, source: str = "ha_action") -> None:
    """Stufe 1: Fire-and-forget Kopie an OC Brain."""
    if not oc_configured():
        return
    try:
        payload = f"[{source.upper()}] {text}"
        ok, msg = await send_message_to_agent_async(payload, agent_id="main", timeout=10.0)
        if ok:
            logger.debug(f"OC Brain Mirror OK: {msg[:80]}")
        else:
            logger.warning(f"OC Brain Mirror fehlgeschlagen: {msg}")
    except Exception as e:
        logger.warning(f"OC Brain Mirror Exception: {e}")

router = APIRouter(prefix="/webhook", tags=["webhooks"])
ha_client = HAClient()

# GQA F2: Scout-Direct-Mode – Steuerbefehle lokal, nur Deep-Reasoning an VPS
SCOUT_DIRECT_MODE = os.getenv("SCOUT_DIRECT_MODE", "false").lower() in ("true", "1", "yes")

class HAActionPayload(BaseModel):
    action: Optional[str] = "text_input"
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

@router.post("/ha_action")
async def receive_ha_action(
    request: Request,
    _auth: None = Depends(verify_ha_auth),
):
    """
    Empfängt interaktive Action-Events oder direkte Text-Eingaben
    von der Home Assistant Companion App (z.B. iPhone).
    """
    try:
        raw_payload = await request.json()
    except Exception:
        raw_payload = {}

    # GQA F13: Entry Adapter – normalisierter Input für Gravitator/Triage
    try:
        entry = normalize_request("ha", raw_payload, auth_ctx={"method": "bearer"})
    except Exception as e:
        logger.error(f"Entry Adapter Normalization Failed: {e}")
        return {"status": "error", "reason": "normalization_failed"}

    # Ring-0: Hugin Input-Triage (Validation Sync - Wrapped in Thread)
    # Hugin acts as the initial Logic Validator on the Strut
    hugin_result = None
    try:
        def _run_hugin():
            from src.logic_core.hugin import triage
            return triage(entry)

        hugin_result = await asyncio.to_thread(_run_hugin)
        logger.info(f"Hugin Triage: mtho={hugin_result.mtho_base} intent={hugin_result.intent} priority={hugin_result.priority}")
    except Exception as e:
        logger.warning(f"Hugin Triage fehlgeschlagen: {e}")

    logger.info(f"Home Assistant Action empfangen: {entry.payload}")

    action = entry.payload.get("action", "")
    message = entry.payload.get("text", "")

    if message:
        logger.info(f"Nachrichtentext: {message}")

    # --- KERNLOGIK FÜR EINGEHENDE BEFEHLE ---

    if action == "mtho_ping":
        reply_text = "MTHO_CORE: Ping empfangen! Brücke zur App funktioniert."
        ha_client.send_mobile_app_notification(reply_text, title="PONG")
        return {"status": "ok", "action": "ping_replied"}

    elif action == "mtho_command" or action == "text_input":
        user_text = message or "Kein Text übermittelt"

        # [TAKT 0 GATE] - Async check before processing
        if not await check_takt_zero():
            logger.warning("TAKT 0 VETO: System rejected HA Action")
            return {"status": "veto", "reason": "system_instability_takt0"}

        # Ring-1 Perf: Sync process_text/triage in Thread → Event-Loop frei
        if SCOUT_DIRECT_MODE:
            from src.services.scout_direct_handler import process_text
            ctx = {"source": "ha_action", "action": action}
            if hugin_result is not None:
                ctx["hugin_triage"] = hugin_result
            result = await asyncio.to_thread(process_text, user_text, ctx)
            reply_text = result["reply"]
        else:
            reply_text = await asyncio.to_thread(_legacy_ha_command_pipeline, user_text)

        ha_client.send_mobile_app_notification(reply_text, title="MTHO_CORE")
        asyncio.create_task(_mirror_to_oc_brain(user_text, "ha_command"))
        return {"status": "ok", "action": "command_processed", "reply": reply_text}

    else:
        logger.warning(f"Unbekannte Action empfangen: {action}")
        return {"status": "ignored", "reason": "Unknown action"}

def _legacy_ha_command_pipeline(user_text: str) -> str:
    """Legacy: Triage → HA/Heavy. Sync, wird via asyncio.to_thread aufgerufen."""
    triage = mtho_llm.run_triage(user_text)
    if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
        domain = triage.target_entity.split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
        service = triage.action or ("turn_on" if "turn_off" not in (triage.intent or "") else "turn_off")
        if triage.intent in ["turn_on", "turn_off", "toggle"]:
            service = triage.intent
        success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity or "")
        return f"Befehl ausgeführt: {service} auf {triage.target_entity}" if success else f"Fehler bei Befehl: {service} auf {triage.target_entity}"
    if triage.intent in ["deep_reasoning", "chat"]:
        sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für MTHO_CORE. Antworte analytisch, auf Systemik fokussiert. Meide neurotypische Floskeln vollständig."
        # Ring-0: Context Injection (context_injector)
        try:
            from src.logic_core.context_injector import inject_context_for_agent, check_semantic_drift, apply_veto
            context_ctx = inject_context_for_agent(user_text, n_results=3, format="markdown")
            if context_ctx:
                sys_prompt += "\n\n## Relevanter Kontext (context field)\n" + context_ctx
            reply = mtho_llm.invoke_heavy_reasoning(sys_prompt, user_text)
            if context_ctx:
                veto = check_semantic_drift(context_ctx, reply)
                if veto.vetoed:
                    apply_veto(veto)
            return reply
        except Exception:
            return mtho_llm.invoke_heavy_reasoning(sys_prompt, user_text)
    return f"[SLM Triage] Unbekannter Intent für: '{user_text}'"


class RawTextPayload(BaseModel):
    text: str


class ForwardedTextPayload(BaseModel):
    """GQA F2: Payload für VPS-Fallback (Scout → VPS bei HA-Ausfall)."""
    text: str
    context: Optional[Dict[str, Any]] = None


def _forwarded_text_pipeline(text: str) -> str:
    """VPS-Fallback Pipeline: Triage → HA/Heavy. Sync, via asyncio.to_thread."""
    triage = mtho_llm.run_triage(text)
    if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
        domain = triage.target_entity.split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
        service = triage.action or ("turn_on" if "turn_off" not in (triage.intent or "") else "turn_off")
        if triage.intent in ["turn_on", "turn_off", "toggle"]:
            service = triage.intent
        success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity or "")
        return f"Befehl ausgeführt (VPS-Fallback): {service} auf {triage.target_entity}" if success else f"Fehler bei Befehl (VPS-Fallback): {service} auf {triage.target_entity}"
    if triage.intent in ["deep_reasoning", "chat"]:
        sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für MTHO_CORE. Antworte analytisch, auf Systemik fokussiert."
        try:
            from src.logic_core.context_injector import inject_context_for_agent, check_semantic_drift, apply_veto
            context_ctx = inject_context_for_agent(text, n_results=3, format="markdown")
            if context_ctx:
                sys_prompt += "\n\n## Relevanter Kontext (context field)\n" + context_ctx
            reply = mtho_llm.invoke_heavy_reasoning(sys_prompt, text)
            if context_ctx:
                veto = check_semantic_drift(context_ctx, reply)
                if veto.vetoed:
                    apply_veto(veto)
            return reply
        except Exception:
            return mtho_llm.invoke_heavy_reasoning(sys_prompt, text)
    return f"[SLM Triage] Unbekannter Intent: '{text}'"


@router.post("/forwarded_text")
async def receive_forwarded_text(
    payload: ForwardedTextPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    GQA F2: VPS-Fallback-Endpoint.
    """
    logger.info("Forwarded Text von Scout empfangen (VPS-Fallback)")

    if not await check_takt_zero():
        return {"status": "veto", "reason": "system_instability_takt0"}

    reply = await asyncio.to_thread(_forwarded_text_pipeline, payload.text)
    return {"status": "ok", "reply": reply, "routed": "vps_fallback"}


@router.post("/assist")
async def assist_pipeline(
    payload: RawTextPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    Assist-Pipeline Endpoint.
    """
    # Note: inject_raw_text handles Takt 0
    result = await inject_raw_text(payload)
    reply = result.get("reply", "")
    if reply:
        try:
            from src.voice.tts_dispatcher import dispatch_tts
            tts_target = os.getenv("TTS_TARGET", "mini").strip().lower()
            await dispatch_tts(text=reply, target=tts_target, role_name="mtho_dialog")
        except Exception as e:
            logger.warning(f"TTS auf Mini fehlgeschlagen: {e}")
    return result


@router.post("/inject_text")
async def inject_raw_text(
    payload: RawTextPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    Empfängt rohe Text-Strings (z.B. von Google Home / Nabu Casa Webhooks)
    und wirft sie direkt in die LLM-Triage-Pipeline.
    """
    logger.info(f"Roher Text-Injekt empfangen: {payload.text}")

    if not await check_takt_zero():
        logger.warning("TAKT 0 VETO: System rejected Text Inject")
        return {"status": "veto", "reason": "system_instability_takt0"}

    if SCOUT_DIRECT_MODE:
        from src.services.scout_direct_handler import process_text
        result = await asyncio.to_thread(process_text, payload.text, {"source": "inject_text"})
        reply_text = result["reply"]
    else:
        reply_text = await asyncio.to_thread(_legacy_ha_command_pipeline, payload.text)

    # Stufe 1: Mirror an OC Brain
    asyncio.create_task(_mirror_to_oc_brain(payload.text, "voice_inject"))
    return {"status": "ok", "action": "voice_processed", "reply": reply_text}
