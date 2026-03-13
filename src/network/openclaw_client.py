# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
OpenClaw Gateway Client (Hostinger).
Liest VPS_HOST und OPENCLAW_GATEWAY_TOKEN aus .env.
- CORE → OC: send_message_to_agent() (POST /v1/responses)
- OC → CORE: GQA F2 Webhook-Push (POST /api/oc/webhook) oder Fallback fetch_oc_submissions (SFTP).
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv
from src.utils.time_metric import get_friction_timeout

load_dotenv()

VPS_HOST = os.getenv("VPS_HOST", "")
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
# OpenClaw Gateway: bei Hostinger oft Container-PORT (z. B. 58105), sonst 18789
OPENCLAW_GATEWAY_PORT = int(os.getenv("OPENCLAW_GATEWAY_PORT", "18789"))

# Pfad auf dem VPS, in dem OC Einreichungen für den Rat ablegt (OC → CORE)
OC_RAT_SUBMISSIONS_DIR = "/var/lib/openclaw/workspace/rat_submissions"


def gateway_url(path: str = "") -> str:
    """Basis-URL des OpenClaw-Gateways (für spätere API-Anbindung)."""
    base = f"http://{VPS_HOST}:{OPENCLAW_GATEWAY_PORT}"
    return f"{base}{path}" if path.startswith("/") else f"{base}/{path}"


def auth_headers() -> dict:
    """Header mit Gateway-Token für authentifizierte Requests."""
    if not OPENCLAW_GATEWAY_TOKEN:
        return {}
    return {"Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}"}


def is_configured() -> bool:
    """True, wenn Host und Token gesetzt sind."""
    return bool(VPS_HOST and OPENCLAW_GATEWAY_TOKEN)


async def check_gateway_async(timeout: float = 5.0) -> tuple[bool, str]:
    """
    Testet die Erreichbarkeit des OpenClaw-Gateways (GET auf Basis-URL).
    Returns: (success, message)
    """
    if not is_configured():
        return False, "Nicht konfiguriert (VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
    try:
        url = gateway_url("/")
        timeout_friction = get_friction_timeout(timeout)
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_friction)) as client:
            r = await client.get(url, headers=auth_headers())
            r.raise_for_status()
            return True, f"OK {r.status_code} – Gateway erreichbar"
    except httpx.TimeoutException:
        return False, "Timeout – Gateway nicht erreichbar"
    except httpx.ConnectError as e:
        return False, f"Verbindungsfehler: {e}"
    except httpx.HTTPStatusError as e:
        return False, f"HTTP {e.response.status_code}: {e}"
    except Exception as e:
        return False, f"Fehler: {e}"


def check_gateway(timeout: float = 5.0) -> tuple[bool, str]:
    """Sync-Wrapper fuer check_gateway_async (Backward-Compat)."""
    return asyncio.run(check_gateway_async(timeout))


async def send_message_to_agent_async(
    text: str,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    """
    Sendet eine Nachricht an einen OC-Agenten (CORE -> OC).
    Nutzt OpenClaw Gateway POST /v1/responses.
    Returns: (success, response_text oder Fehlermeldung)
    """
    if not is_configured():
        return False, "Nicht konfiguriert (VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
    try:
        url = gateway_url("/v1/responses")
        headers = {
            **auth_headers(),
            "Content-Type": "application/json",
            "x-openclaw-agent-id": agent_id,
        }
        body: dict = {"model": "openclaw", "input": text}
        if user:
            body["user"] = user
        timeout_friction = get_friction_timeout(timeout)
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_friction)) as client:
            r = await client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
            out = data.get("output") or []
            parts = []
            for item in out if isinstance(out, list) else []:
                if isinstance(item, dict):
                    if item.get("type") == "output_text" and "text" in item:
                        parts.append(item["text"])
                    if item.get("type") == "content_part" and "text" in item:
                        parts.append(item["text"])
            response_text = "".join(parts).strip() if parts else str(data)[:500]
            return True, response_text or "(leere Antwort)"
    except httpx.TimeoutException:
        return False, "Timeout – Gateway hat nicht rechtzeitig geantwortet"
    except httpx.ConnectError as e:
        return False, f"Verbindungsfehler: {e}"
    except httpx.HTTPStatusError as e:
        err_msg = e.response.text[:300] if e.response is not None else str(e)
        return False, f"HTTP {e.response.status_code if e.response else 0}: {err_msg}"
    except Exception as e:
        return False, f"Fehler: {e}"


def send_message_to_agent(
    text: str,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    """Sync-Wrapper fuer send_message_to_agent_async (Backward-Compat)."""
    return asyncio.run(send_message_to_agent_async(text, agent_id, user, timeout))


async def send_event_to_oc_brain_async(
    event_type: str,
    data: dict,
    timeout: float = 15.0,
) -> tuple[bool, str]:
    """
    Sendet ein CORE-Event an OC Brain (strukturiert).
    Nutzt intern send_message_to_agent_async() mit Prefix-Formatierung.
    """
    import json as _json

    formatted_msg = f"[CORE_EVENT] type={event_type}\n{_json.dumps(data, ensure_ascii=False, indent=2)}"
    return await send_message_to_agent_async(
        text=formatted_msg,
        agent_id="main",
        user="core_event_bus",
        timeout=timeout,
    )


def send_event_to_oc_brain(
    event_type: str,
    data: dict,
    timeout: float = 15.0,
) -> tuple[bool, str]:
    """Sync-Wrapper fuer send_event_to_oc_brain_async (Backward-Compat)."""
    return asyncio.run(send_event_to_oc_brain_async(event_type, data, timeout))
