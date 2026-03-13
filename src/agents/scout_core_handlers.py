# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Scout Ephemeral Handlers: Intent-Handler fuer Ephemeral Agents.

Registriert Handler fuer:
- COMMAND: HA-Steuerung via scout_direct_handler
- DEEP_REASONING: OC Brain / Gemini Heavy
- VISION_ANALYSIS: Gemini Vision (Brio/Daemon Output)
- TTS_DISPATCH: Sprache auf Mini/WhatsApp
- FAILOVER: VPS-Routing bei Dreadnought-Ausfall
"""
from __future__ import annotations

import os
from typing import Any
from loguru import logger

from .core_agent import IntentType, EphemeralAgentPool, get_ephemeral_pool


async def handle_command(payload: dict) -> dict:
    """
    COMMAND Intent: Fuehrt HA-Service-Call aus.
    Payload: {text: str, entities?: list}
    Nutzt process_text_async wenn verfuegbar, sonst asyncio.to_thread(process_text).
    """
    text = payload.get("text", "")
    context = payload.get("context", {})
    try:
        from src.services.scout_direct_handler import process_text
        import asyncio
        return await asyncio.to_thread(process_text, text, context)
    except Exception as e:
        logger.error(f"Fehler in handle_command (sync fallback): {e}")
        return {"error": str(e), "success": False}


async def handle_deep_reasoning(payload: dict) -> dict:
    """
    DEEP_REASONING Intent: OC Brain oder lokales Heavy Reasoning.
    Payload: {text: str, context?: dict}
    """
    text = payload.get("text", "")
    try:
        from src.network.openclaw_client import send_message_to_agent_async, is_configured
        if is_configured():
            ok, reply = await send_message_to_agent_async(text, agent_id="main", timeout=60.0)
            if ok:
                return {"reply": reply, "source": "oc_brain", "success": True}
    except Exception as e:
        logger.warning(f"OC Brain nicht erreichbar: {e}")

    try:
        from src.ai.llm_interface import core_llm
        reply = core_llm.invoke_heavy_reasoning(
            "Du bist CORE. Antworte praezise und analytisch.",
            text
        )
        return {"reply": reply, "source": "gemini_heavy", "success": True}
    except Exception as e:
        return {"reply": str(e), "source": "error", "success": False}


async def handle_vision_analysis(payload: dict) -> dict:
    """
    VISION_ANALYSIS Intent: Analysiert Bild/Frame mit Gemini Vision.
    Payload: {image_path: str} oder {image_bytes: bytes}
    """
    image_path = payload.get("image_path")
    if not image_path or not os.path.isfile(image_path):
        return {"error": "Kein gueltiger Bildpfad", "success": False}

    try:
        from src.ai.brio_image_analyzer import analyze_image
        result = analyze_image(image_path)
        return {"analysis": result, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


async def handle_tts_dispatch(payload: dict) -> dict:
    """
    TTS_DISPATCH Intent: Text-to-Speech auf Target.
    Payload: {text: str, target?: "mini"|"elevenlabs"|"piper"|"whatsapp"}
    """
    text = payload.get("text", "")
    target = payload.get("target", "mini")

    if not text:
        return {"error": "Kein Text", "success": False}

    try:
        from src.voice.tts_dispatcher import dispatch_tts
        result = await dispatch_tts(text, target=target)
        return {"dispatched": True, "target": target, "success": result}
    except Exception as e:
        return {"error": str(e), "success": False}


async def handle_failover(payload: dict) -> dict:
    """
    FAILOVER Intent: Routing an VPS wenn Dreadnought offline.
    Payload: {text: str, context?: dict}
    """
    text = payload.get("text", "")
    context = payload.get("context", {})

    vps_url = (os.getenv("CORE_VPS_URL") or "").strip().rstrip("/")
    if not vps_url:
        return {"error": "CORE_VPS_URL nicht konfiguriert", "success": False}

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{vps_url}/webhook/forwarded_text",
                json={"text": text, "context": context},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status < 400:
                    data = await resp.json()
                    return {"reply": data.get("reply", ""), "source": "vps", "success": True}
                return {"error": f"VPS Fehler: {resp.status}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def register_all_handlers(pool: EphemeralAgentPool | None = None):
    """Registriert alle Scout Ephemeral Handlers im Pool."""
    pool = pool or get_ephemeral_pool()
    pool.register_handler(IntentType.COMMAND, handle_command)
    pool.register_handler(IntentType.DEEP_REASONING, handle_deep_reasoning)
    pool.register_handler(IntentType.VISION_ANALYSIS, handle_vision_analysis)
    pool.register_handler(IntentType.TTS_DISPATCH, handle_tts_dispatch)
    pool.register_handler(IntentType.FAILOVER, handle_failover)
    logger.info("[SCOUT-EPHEMERAL] Alle Handler registriert")


async def scout_fusion_init():
    """
    Initialisiert das Scout-Fusion-Protokoll:
    - Registriert Ephemeral Handlers
    - Startet GC Loop
    """
    pool = get_ephemeral_pool()
    register_all_handlers(pool)
    await pool.start_gc_loop()
    logger.info("[SCOUT-FUSION] Ephemeral Agent Pool aktiv")
    return pool
