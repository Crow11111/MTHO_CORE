"""
GQA Refactor F2 - scout-direct-handler
======================================
Lokaler Handler auf Scout: Steuerbefehle direkt verarbeiten, Deep-Reasoning an OC Brain.
Fallback: Wenn lokale HA nicht erreichbar → Route über VPS.

Routing:
- command/turn_on/turn_off/toggle → HA lokal (Scout)
- deep_reasoning/chat → OC Brain (VPS)
- HA unreachable → Fallback an ATLAS_VPS_URL (falls konfiguriert)

Env: SCOUT_DIRECT_MODE, ATLAS_VPS_URL, HA_WEBHOOK_TOKEN, HASS_URL, HASS_TOKEN
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# SSL-Warnung unterdrücken für VPS-Fallback (self-signed)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Env: SCOUT_DIRECT_MODE=true aktiviert diesen Handler; ATLAS_VPS_URL für Fallback
ATLAS_VPS_URL = (os.getenv("ATLAS_VPS_URL") or "").strip().rstrip("/")
HA_WEBHOOK_TOKEN = os.getenv("HA_WEBHOOK_TOKEN", "").strip()


def _load_ha_client():
    """Lazy load HAClient (nur bei Bedarf)."""
    from src.network.ha_client import HAClient
    return HAClient()


def _load_triage():
    """Lazy load Triage (nur bei Bedarf)."""
    from src.ai.llm_interface import atlas_llm
    return atlas_llm


def _forward_to_vps(text: str, context: dict) -> tuple[bool, str]:
    """
    Leitet Anfrage an VPS weiter (Fallback bei HA-Ausfall oder Deep-Reasoning).
    POST an ATLAS_VPS_URL/webhook/forwarded_text
    """
    if not ATLAS_VPS_URL:
        return False, "VPS-Fallback nicht konfiguriert (ATLAS_VPS_URL)"
    url = f"{ATLAS_VPS_URL}/webhook/forwarded_text"
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

    # --- DEEP REASONING / CHAT → OC Brain (VPS) direkt ---
    if triage.intent in ("deep_reasoning", "chat"):
        try:
            from src.network.openclaw_client import send_message_to_agent, is_configured
            if is_configured():
                ok, reply = send_message_to_agent(text, agent_id="main", timeout=60.0)
                if ok:
                    return {"reply": reply, "success": True, "routed": "vps_reasoning"}
        except Exception as e:
            logger.warning("OC Brain Aufruf fehlgeschlagen: {}", e)
        # Fallback: lokaler Heavy-Layer (Gemini)
        try:
            from src.ai.llm_interface import atlas_llm
            sys_prompt = "Du bist Virtual Marc, Kopf des Osmium Councils für ATLAS_CORE. Antworte analytisch, auf Systemik fokussiert."
            reply = atlas_llm.invoke_heavy_reasoning(sys_prompt, text)
            return {"reply": reply, "success": True, "routed": "local"}
        except Exception as e:
            logger.error("Heavy Reasoning fallback fehlgeschlagen: {}", e)
            return {"reply": f"OC Brain nicht erreichbar. Lokaler Fallback fehlgeschlagen: {e}", "success": False, "routed": "local"}

    # --- UNBEKANNT ---
    return {"reply": f"[SLM Triage] Unbekannter Intent für: '{text}'", "success": False, "routed": "local"}
