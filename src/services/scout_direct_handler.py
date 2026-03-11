# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
GQA Refactor F2 - scout-direct-handler
======================================
Lokaler Handler auf Scout: Steuerbefehle direkt verarbeiten, Deep-Reasoning an OC Brain.
Fallback: Wenn lokale HA nicht erreichbar → Route über VPS.

SCOUT-FUSION Update: Ephemeral Agent Integration (Signal-Vektor 2 / INTENT)
- Ephemeral Agents werden bei deep_reasoning gespawnt
- Async-Variante fuer HA Conversation Agent

Routing:
- command/turn_on/turn_off/toggle → HA lokal (Scout)
- deep_reasoning/chat → Ephemeral Agent → OC Brain (VPS)
- HA unreachable → Fallback an MTHO_VPS_URL (falls konfiguriert)

Voice: Smart Command Parser (src/voice/smart_command_parser) wird bevorzugt,
       wenn entities verfügbar sind – unterstützt Helligkeit, Farbe, Temperatur.

Env: SCOUT_DIRECT_MODE, MTHO_VPS_URL, HA_WEBHOOK_TOKEN, HASS_URL, HASS_TOKEN
"""
from __future__ import annotations

import json
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# SSL-Warnung unterdrücken für VPS-Fallback (self-signed)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Env: SCOUT_DIRECT_MODE=true aktiviert diesen Handler; MTHO_VPS_URL für Fallback
MTHO_VPS_URL = (os.getenv("MTHO_VPS_URL") or "").strip().rstrip("/")
HA_WEBHOOK_TOKEN = os.getenv("HA_WEBHOOK_TOKEN", "").strip()
DEFAULT_MEDIA_PLAYER = os.getenv("DEFAULT_MEDIA_PLAYER", "").strip()


def _load_ha_client():
    """Lazy load HAClient (nur bei Bedarf)."""
    from src.network.ha_client import HAClient
    return HAClient()


def _load_triage():
    """Lazy load Triage (nur bei Bedarf)."""
    from src.ai.llm_interface import mtho_llm
    return mtho_llm


def _forward_to_vps(text: str, context: dict) -> tuple[bool, str]:
    """
    Leitet Anfrage an VPS weiter (Fallback bei HA-Ausfall oder Deep-Reasoning).
    POST an MTHO_VPS_URL/webhook/forwarded_text
    """
    if not MTHO_VPS_URL:
        return False, "VPS-Fallback nicht konfiguriert (MTHO_VPS_URL)"
    url = f"{MTHO_VPS_URL}/webhook/forwarded_text"
    try:
        import requests
        headers = {"Content-Type": "application/json"}
        if HA_WEBHOOK_TOKEN:
            headers["Authorization"] = f"Bearer {HA_WEBHOOK_TOKEN}"
        r = requests.post(url, json={"text": text, "context": context}, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json()
        return True, data.get("reply", data.get("message", str(data)))
    except Exception as e:
        logger.error("VPS-Fallback fehlgeschlagen: {}", e)
        return False, str(e)


def _call_ha_service(domain: str, service: str, entity_id: str, service_data: dict | None = None) -> bool:
    """Ruft HA-Service auf. Returns True bei Erfolg."""
    try:
        ha = _load_ha_client()
        return ha.call_service(domain, service, entity_id, service_data)
    except Exception as e:
        logger.error("HA Service-Aufruf fehlgeschlagen: {}", e)
        return False

async def _speak_response(reply: str):
    """Gibt eine Antwort über den Standard-Media-Player aus."""
    if not DEFAULT_MEDIA_PLAYER:
        logger.warning("Kein DEFAULT_MEDIA_PLAYER in .env konfiguriert. Sprachausgabe übersprungen.")
        return

    try:
        from src.connectors.home_assistant import HomeAssistantClient
        ha_client = HomeAssistantClient()
        await ha_client.speak(DEFAULT_MEDIA_PLAYER, reply)
    except Exception as e:
        logger.error(f"Fehler bei der Sprachausgabe: {e}")



def _load_entities_for_parser(context: dict) -> list:
    """Lädt HA-Entities für Smart Parser (Cache oder Context)."""
    if context.get("entities"):
        return context["entities"]
    try:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, "data", "home_assistant", "states.json")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.debug("Entities-Cache nicht geladen: {}", e)
    return []


def process_text(text: str, context: dict | None = None) -> dict:
    """
    Hauptlogik: Triage → Command lokal oder Deep-Reasoning an VPS.
    Fallback: Wenn HA nicht erreichbar, an VPS weiterleiten.

    Returns: {"reply": str, "success": bool, "routed": "local"|"vps_fallback"|"vps_reasoning"}
    """
    context = context or {}
    text = (text or "").strip()
    if not text:
        return {"reply": "Kein Text eingegeben.", "success": False, "routed": "local"}

    # --- SMART COMMAND PARSER (Voice) – bevorzugt bei Steuerbefehlen ---
    entities = _load_entities_for_parser(context)
    try:
        from src.voice.smart_command_parser import parse_command

        ha_action = parse_command(text, entities, skip_llm_fallback=True)
        if ha_action and ha_action.entity_id:
            success = _call_ha_service(
                ha_action.domain,
                ha_action.service,
                ha_action.entity_id,
                ha_action.data if ha_action.data else None,
            )
            if success:
                reply = f"Befehl ausgeführt: {ha_action.service} auf {ha_action.entity_id.replace('_', ' ')}"
                # Asynchrone Sprachausgabe im Hintergrund starten
                import asyncio
                asyncio.create_task(_speak_response(reply))
                return {
                    "reply": reply,
                    "success": True,
                    "routed": "local",
                }
            # Smart Parser hatte Match, aber HA-Call fehlgeschlagen → VPS-Fallback
            logger.warning("Smart Parser Match, HA-Call fehlgeschlagen, versuche VPS-Fallback")
            ok, reply = _forward_to_vps(text, context)
            return {"reply": reply, "success": ok, "routed": "vps_fallback"}
    except Exception as e:
        logger.debug("Smart Parser nicht genutzt, Fallback auf Triage: {}", e)

    # --- LEGACY: Hugin/LLM Triage ---
    triage = _load_triage().run_triage(text)

    # --- COMMAND PATH ---
    if triage.intent in ("command", "turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off"):
        domain = (triage.target_entity or "homeassistant").split(".")[0] if "." in (triage.target_entity or "") else "homeassistant"
        service = triage.action or ("turn_on" if "turn_off" not in (triage.intent or "") else "turn_off")
        if triage.action:
            service = triage.action
        elif triage.intent in ("turn_on", "turn_off", "toggle"):
            service = triage.intent
        else:
            service = "turn_on"
        entity_id = triage.target_entity or ""

        if not entity_id:
            return {"reply": "Keine Ziel-Entity erkannt.", "success": False, "routed": "local"}

        success = _call_ha_service(domain, service, entity_id)
        if success:
            return {
                "reply": f"Befehl ausgeführt: {service} auf {entity_id}",
                "success": True,
                "routed": "local",
            }
        # Fallback: HA nicht erreichbar → VPS
        logger.warning("Lokale HA nicht erreichbar, versuche VPS-Fallback")
        ok, reply = _forward_to_vps(text, context)
        return {
            "reply": reply,
            "success": ok,
            "routed": "vps_fallback",
        }

    # --- DEEP REASONING / CHAT → LOKALES HEAVY REASONING (Ollama/Gemini-Fallback) ---
    if triage.intent in ("deep_reasoning", "chat"):
        logger.info("Deep Reasoning angefordert. Nutze lokalen Heavy Layer.")
        # VPS-Pfad ist temporaer deaktiviert (Hephaistos-Protokoll: Autonomie erzwingen)

        # Lokaler Heavy-Layer (Ollama konfiguriert in llm_interface.py)
        try:
            from src.ai.llm_interface import mtho_llm
            from src.logic_core.context_injector import inject_context_for_agent, check_semantic_drift, apply_veto
            sys_prompt = "Du bist OMEGA, die Kern-Intelligenz für MTHO_CORE. Antworte analytisch, direkt und auf Systemik fokussiert."

            # Ring-0: Context Injection (context_injector)
            context_ctx = inject_context_for_agent(text, n_results=3, format="markdown")
            if context_ctx:
                sys_prompt += "\n\n## Relevanter Kontext (context field)\n" + context_ctx

            reply = mtho_llm.invoke_heavy_reasoning(sys_prompt, text)

            # Ring-0: Drift Veto (Semantic Drift Block)
            if context_ctx:
                veto = check_semantic_drift(context_ctx, reply)
                if veto.vetoed:
                    apply_veto(veto)
                    logger.warning("Drift Veto: Semantic Drift erkannt, z_widerstand erhöht")

            # Sprachausgabe für Deep Reasoning Antworten asynchron starten
            import asyncio
            asyncio.create_task(_speak_response(reply))

            return {"reply": reply, "success": True, "routed": "local_heavy"}

        except Exception as e:
            logger.error("Heavy Reasoning fallback fehlgeschlagen: {}", e)
            return {"reply": f"Lokale KI-Verarbeitung fehlgeschlagen: {e}", "success": False, "routed": "local"}

    # --- UNBEKANNT ---
    return {"reply": f"[SLM Triage] Unbekannter Intent für: '{text}'", "success": False, "routed": "local"}


# ============================================================================
# EPHEMERAL AGENT INTEGRATION (Async / Scout-Fusion)
# ============================================================================

async def process_text_async(text: str, context: dict | None = None) -> dict:
    """
    Async-Variante von process_text mit Ephemeral Agent Integration.
    Spawnt kurzlebige Sub-Instanzen fuer Intent-Verarbeitung.
    """
    context = context or {}
    text = (text or "").strip()
    if not text:
        return {"reply": "Kein Text eingegeben.", "success": False, "routed": "local"}

    try:
        from src.agents.mtho_agent import IntentType, get_ephemeral_pool
        from src.agents.scout_mtho_handlers import register_all_handlers

        pool = get_ephemeral_pool()
        if pool.active_count == 0 and not pool._handlers:
            register_all_handlers(pool)

        triage = _load_triage().run_triage(text)

        intent_type = IntentType.COMMAND
        if triage.intent in ("deep_reasoning", "chat"):
            intent_type = IntentType.DEEP_REASONING
        elif triage.intent in ("command", "turn_on", "turn_off", "toggle"):
            intent_type = IntentType.COMMAND

        payload = {"text": text, "context": context, "triage": triage.__dict__ if hasattr(triage, '__dict__') else {}}
        result = await pool.spawn_and_execute(intent_type, payload, ttl=30.0)

        if result.success:
            reply = result.payload.get("reply", str(result.payload)) if isinstance(result.payload, dict) else str(result.payload)
            return {
                "reply": reply,
                "success": True,
                "routed": f"ephemeral_{intent_type.value}",
                "duration_ms": result.duration_ms
            }
        else:
            logger.warning(f"Ephemeral Agent failed: {result.error}, sync fallback")
            return process_text(text, context)

    except Exception as e:
        logger.warning(f"Ephemeral Agent Integration nicht verfuegbar: {e}, sync fallback")
        return process_text(text, context)
