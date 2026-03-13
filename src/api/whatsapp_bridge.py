# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException, BackgroundTasks
from src.services.audio_service import audio_service
from src.services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

def verify_token() -> str:
    token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    if not token:
        logger.error("WHATSAPP_VERIFY_TOKEN is missing")
    return token or ""

@router.get("/")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token():
            return Response(content=challenge, media_type="text/plain")
        raise HTTPException(status_code=403, detail="Forbidden")
    raise HTTPException(status_code=400, detail="Bad Request")

@router.post("/")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body: Dict[str, Any] = await request.json()
        logger.info(f"WhatsApp webhook payload received")
        
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for message in value["messages"]:
                            # Asynchroner offload der Nachricht-Verarbeitung um Latenz gering zu halten (4vCPU Optimierung)
                            background_tasks.add_task(process_incoming_message, message)
        
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook payload: {str(e)}")
        # Stets 200 zurueckgeben, andernfalls stoppt Meta das Senden von Webhooks
        return Response(status_code=200)

async def process_incoming_message(message: Dict[str, Any]):
    msg_id = message.get("id")
    msg_type = message.get("type")
    sender = message.get("from")
    logger.info(f"Processing message {msg_id} of type {msg_type} from {sender}")

    if msg_type == "text":
        text_body = message.get("text", {}).get("body", "").lower()
        if "hallo" in text_body or "init" in text_body:
            logger.info("Triggering audio greeting...")
            audio_bytes = await audio_service.generate_speech("Initialisierung abgeschlossen. Willkommen im System.", role="strict")
            if audio_bytes:
                await notification_service.send_audio_message(to=sender, audio_bytes=audio_bytes)
