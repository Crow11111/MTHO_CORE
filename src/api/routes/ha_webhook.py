"""
GQA Refactor F2 - scout-direct-handler
Steuerbefehle lokal auf Scout; Deep-Reasoning an OC Brain.
SCOUT_DIRECT_MODE=true → ScoutDirectHandler (lokale HA, VPS-Fallback).
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from src.api.auth_webhook import verify_ha_auth
from src.api.entry_adapter import normalize_request
from typing import Optional, Dict, Any
from loguru import logger
from src.network.ha_client import HAClient
from src.ai.llm_interface import atlas_llm
import os

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
    entry = normalize_request("ha", raw_payload, auth_ctx={"method": "bearer"})
    logger.info(f"Home Assistant Action empfangen: {entry.payload}")
    
    action = entry.payload.get("action", "")
    message = entry.payload.get("text", "")
    
    if message:
        logger.info(f"Nachrichtentext: {message}")
        
    # --- KERNLOGIK FÜR EINGEHENDE BEFEHLE ---
    
    if action == "atlas_ping":
        # Simpler Test-Ping über einen Button
        reply_text = "ATLAS_CORE: Ping empfangen! Brücke zur App funktioniert."
        ha_client.send_mobile_app_notification(reply_text, title="PONG")
        return {"status": "ok", "action": "ping_replied"}
        
    elif action == "atlas_command" or action == "text_input":
        user_text = message or "Kein Text übermittelt"

        # GQA F2: Scout-Direct-Mode – lokale HA, VPS-Fallback, Deep-Reasoning an OC Brain
        if SCOUT_DIRECT_MODE:
            from src.services.scout_direct_handler import process_text
            result = process_text(user_text, {"source": "ha_action", "action": action})
            reply_text = result["reply"]
        else:
            # Legacy: Vollständige Pipeline über Dreadnought/VPS
            triage = atlas_llm.run_triage(user_text)
            if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
                domain = triage.target_entity.split(".")[0] if "." in triage.target_entity else "homeassistant"
                if triage.action:
                    service = triage.action
                elif triage.intent in ["turn_on", "turn_off", "toggle"]:
                    service = triage.intent
                else:
                    service = "turn_on"
                success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity)
                reply_text = f"Befehl ausgeführt: {service} auf {triage.target_entity}" if success else f"Fehler bei Befehl: {service} auf {triage.target_entity}"
            elif triage.intent in ["deep_reasoning", "chat"]:
                sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für ATLAS_CORE. Antworte analytisch, auf Systemik fokussiert. Meide neurotypische Floskeln vollständig."
                reply_text = atlas_llm.invoke_heavy_reasoning(sys_prompt, user_text)
            else:
                reply_text = f"[SLM Triage] Unbekannter Intent für: '{user_text}'"

        ha_client.send_mobile_app_notification(reply_text, title="ATLAS_CORE")
        return {"status": "ok", "action": "command_processed", "reply": reply_text}

    else:
        logger.warning(f"Unbekannte Action empfangen: {action}")
        return {"status": "ignored", "reason": "Unknown action"}

class RawTextPayload(BaseModel):
    text: str


class ForwardedTextPayload(BaseModel):
    """GQA F2: Payload für VPS-Fallback (Scout → VPS bei HA-Ausfall)."""
    text: str
    context: Optional[Dict[str, Any]] = None


@router.post("/forwarded_text")
async def receive_forwarded_text(
    payload: ForwardedTextPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    GQA F2: VPS-Fallback-Endpoint.
    Scout leitet hierher weiter, wenn lokale HA nicht erreichbar.
    Verarbeitet mit voller Pipeline (HASS_URL auf VPS zeigt auf Scout-HA via Nabu Casa/Tunnel).
    """
    logger.info("Forwarded Text von Scout empfangen (VPS-Fallback)")
    # Volle Pipeline – HASS_URL auf VPS muss auf Scout-HA zeigen
    triage = atlas_llm.run_triage(payload.text)
    if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
        domain = triage.target_entity.split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
        service = triage.action or ("turn_on" if "turn_off" not in (triage.intent or "") else "turn_off")
        if triage.intent in ["turn_on", "turn_off", "toggle"]:
            service = triage.intent
        success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity or "")
        reply = f"Befehl ausgeführt (VPS-Fallback): {service} auf {triage.target_entity}" if success else f"Fehler bei Befehl (VPS-Fallback): {service} auf {triage.target_entity}"
    elif triage.intent in ["deep_reasoning", "chat"]:
        sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für ATLAS_CORE. Antworte analytisch, auf Systemik fokussiert."
        reply = atlas_llm.invoke_heavy_reasoning(sys_prompt, payload.text)
    else:
        reply = f"[SLM Triage] Unbekannter Intent: '{payload.text}'"
    return {"status": "ok", "reply": reply, "routed": "vps_fallback"}


@router.post("/assist")
async def assist_pipeline(
    payload: RawTextPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    Assist-Pipeline Endpoint: Empfängt transkribierten Text von HA Assist
    (Whisper STT) und leitet ihn in die Triage-Pipeline. Antwort wird per
    TTS auf dem Mini-Speaker ausgegeben.
    """
    result = await inject_raw_text(payload)
    reply = result.get("reply", "")
    if reply:
        try:
            from src.voice.tts_dispatcher import dispatch_tts
            await dispatch_tts(text=reply, target="mini", role_name="atlas_dialog")
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

    # GQA F2: Scout-Direct-Mode
    if SCOUT_DIRECT_MODE:
        from src.services.scout_direct_handler import process_text
        result = process_text(payload.text, {"source": "inject_text"})
        reply_text = result["reply"]
    else:
        triage = atlas_llm.run_triage(payload.text)
        if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
            domain = triage.target_entity.split(".")[0] if "." in triage.target_entity else "homeassistant"
            if triage.action:
                service = triage.action
            elif triage.intent in ["turn_on", "turn_off", "toggle"]:
                service = triage.intent
            else:
                service = "turn_on"
            success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity)
            reply_text = f"Voice Befehl ausgeführt: {service} auf {triage.target_entity}" if success else f"Fehler bei Voice Befehl: {service} auf {triage.target_entity}"
        elif triage.intent in ["deep_reasoning", "chat"]:
            sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für ATLAS_CORE. Antworte analytisch, auf Systemik fokussiert."
            reply_text = atlas_llm.invoke_heavy_reasoning(sys_prompt, payload.text)
        else:
            reply_text = f"Konnte Google Home Voice nicht einordnen: '{payload.text}'"

    return {"status": "ok", "action": "voice_processed", "reply": reply_text}
