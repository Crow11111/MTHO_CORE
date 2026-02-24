from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from loguru import logger
from src.network.ha_client import HAClient
from src.ai.llm_interface import atlas_llm
import os

router = APIRouter(prefix="/webhook", tags=["webhooks"])
ha_client = HAClient()

class HAActionPayload(BaseModel):
    action: Optional[str] = "text_input"
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

@router.post("/ha_action")
async def receive_ha_action(request: Request):
    """
    Empfängt interaktive Action-Events oder direkte Text-Eingaben 
    von der Home Assistant Companion App (z.B. iPhone).
    """
    try:
        raw_payload = await request.json()
    except Exception:
        raw_payload = {}
        
    logger.info(f"Home Assistant Action empfangen: {raw_payload}")
    
    action = raw_payload.get("action", "")
    message = raw_payload.get("message", "")
    
    if message:
        logger.info(f"Nachrichtentext: {message}")
        
    # --- KERNLOGIK FÜR EINGEHENDE BEFEHLE ---
    
    if action == "atlas_ping":
        # Simpler Test-Ping über einen Button
        reply_text = "ATLAS_CORE: Ping empfangen! Brücke zur App funktioniert."
        ha_client.send_mobile_app_notification(reply_text, title="PONG")
        return {"status": "ok", "action": "ping_replied"}
        
    elif action == "atlas_command" or action == "text_input":
        # Text-Befehl (z.B. Sprachnachricht via Assist oder Textfeld)
        user_text = message or "Kein Text übermittelt"
        
        # 1. Routing Triage (Tier 3 SLM)
        triage = atlas_llm.run_triage(user_text)
        
        if triage.intent == "command" or triage.intent in ["turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"]:
            domain = triage.target_entity.split(".")[0] if "." in triage.target_entity else "homeassistant"
            
            # SLM Hallucination Fallback: If intent holds the service, move it to action
            if triage.action:
                service = triage.action
            elif triage.intent in ["turn_on", "turn_off", "toggle"]:
                service = triage.intent
            else:
                service = "turn_on"
            
            success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity)
            if success:
                reply_text = f"Befehl ausgeführt: {service} auf {triage.target_entity}"
            else:
                reply_text = f"Fehler bei Befehl: {service} auf {triage.target_entity}"
        elif triage.intent in ["deep_reasoning", "chat"]:
            # 2. Heavy Reasoning (Tier 5 Gemini / Virtual Marc)
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

@router.post("/inject_text")
async def inject_raw_text(payload: RawTextPayload):
    """
    Empfängt rohe Text-Strings (z.B. von Google Home / Nabu Casa Webhooks) 
    und wirft sie direkt in die LLM-Triage-Pipeline.
    """
    logger.info(f"Roher Text-Injekt empfangen: {payload.text}")
    
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
        if success:
            reply_text = f"Voice Befehl ausgeführt: {service} auf {triage.target_entity}"
        else:
            reply_text = f"Fehler bei Voice Befehl: {service} auf {triage.target_entity}"
    elif triage.intent in ["deep_reasoning", "chat"]:
        sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für ATLAS_CORE. Antworte analytisch, auf Systemik fokussiert."
        reply_text = atlas_llm.invoke_heavy_reasoning(sys_prompt, payload.text)
    else:
        reply_text = f"Konnte Google Home Voice nicht einordnen: '{payload.text}'"

    return {"status": "ok", "action": "voice_processed", "reply": reply_text}
