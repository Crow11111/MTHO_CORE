from fastapi import APIRouter, Request, BackgroundTasks
from loguru import logger
from src.network.ha_client import HAClient
from src.ai.whatsapp_audio_processor import process_whatsapp_audio
from src.ai.llm_interface import atlas_llm
import os
import json
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

router = APIRouter(prefix="/webhook", tags=["webhooks"])
ha_client = HAClient()


@router.post("/whatsapp")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    """
    Empfängt WhatsApp-Nachrichten über Home Assistant.
    Erkennt Text- und Sprachnachrichten und leitet sie an Gemini weiter.
    """
    raw = await request.json()

    # HA rest_command serialisiert den Payload manchmal doppelt (JSON-String statt Dict)
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
    else:
        payload = raw

    logger.info(f"WhatsApp Webhook: {json.dumps(payload, ensure_ascii=False)[:500]}")

    # Sender extrahieren
    sender = (
        payload.get("key", {}).get("remoteJid") or
        payload.get("sender") or
        payload.get("from", "unknown")
    ) if isinstance(payload, dict) else "unknown"

    message = payload.get("message", {}) if isinstance(payload, dict) else {}

    # ── Sprachnachricht ───────────────────────────────────────────────────────
    audio_msg = message.get("audioMessage") or message.get("pttMessage")

    if audio_msg:
        seconds = audio_msg.get("seconds", 0) if isinstance(audio_msg, dict) else 0
        logger.success(f"🎤 Sprachnachricht von {sender} ({seconds}s)!")

        # Sofort Bestätigung — Pipeline läuft im Hintergrund ([Scout] = leichte Systemantwort)
        ha_client.send_whatsapp(
            to_number=sender,
            text=f"[Scout] 🎤 Sprachmemo ({seconds}s) empfangen. Analysiere..."
        )

        async def run_audio():
            result = await process_whatsapp_audio(audio_msg, sender)
            # [ATLAS] = Antwort vom vollen Modell (Dreadnought)
            ha_client.send_whatsapp(to_number=sender, text=f"[ATLAS] {result}")

        background_tasks.add_task(run_audio)
        return {"status": "audio_processing", "sender": sender, "seconds": seconds}

    # ── Textnachricht ─────────────────────────────────────────────────────────
    text = (
        message.get("conversation") or
        message.get("extendedTextMessage", {}).get("text") or
        payload.get("body") or
        payload.get("text", "")
    )

    if text:
        logger.success(f"💬 Textnachricht von {sender}: {text}")
        
        # Triage → Command oder Reasoning (gleiche Pipeline wie ha_action)
        triage = atlas_llm.run_triage(text)
        
        if triage.intent == "command":
            # Steuerbefehl (HA) → [Scout]: kleines Modell / direkte Bestätigung
            domain = triage.target_entity.split(".")[0] if "." in triage.target_entity else "homeassistant"
            service = triage.action or "turn_on"
            success = ha_client.call_service(domain=domain, service=service, entity_id=triage.target_entity)
            reply = f"[Scout] ✅ {service} → {triage.target_entity}" if success else f"[Scout] ❌ Fehler: {service} → {triage.target_entity}"
        elif triage.intent in ["deep_reasoning", "chat"]:
            # Schwere KI (Dreadnought) → [ATLAS]
            sys_prompt = "Du bist ATLAS, ein intelligenter Assistent. Antworte präzise und knapp auf WhatsApp."
            reply = atlas_llm.invoke_heavy_reasoning(sys_prompt, text)
            reply = f"[ATLAS] {reply}" if reply else "[ATLAS] (keine Antwort)"
        else:
            reply = f"[Scout] Nicht verstanden: '{text}'"
        
        ha_client.send_whatsapp(to_number=sender, text=reply)
        return {"status": "text_handled", "sender": sender, "intent": triage.intent}

    # ── Unbekannt ─────────────────────────────────────────────────────────────
    logger.warning(f"Unbekannter Payload: {list(payload.keys()) if isinstance(payload, dict) else type(payload)}")
    return {"status": "unknown", "keys": list(payload.keys()) if isinstance(payload, dict) else []}
