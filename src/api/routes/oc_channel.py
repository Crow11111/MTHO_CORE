"""
Schnittstelle ATLAS ↔ OC (OpenClaw) im laufenden Backend.

Wird mit dem Backend angeboten; Dev Agent oder andere Komponenten können
damit testweise Nachrichten austauschen und Einreichungen abholen, ohne
Skripte von Hand zu starten.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/oc", tags=["oc-channel"])


class SendBody(BaseModel):
    text: str
    agent_id: str = "main"
    user: str | None = None


@router.get("/status")
def oc_status():
    """Prüft, ob das OpenClaw-Gateway erreichbar und konfiguriert ist."""
    from src.network.openclaw_client import check_gateway, is_configured

    if not is_configured():
        return {"ok": False, "message": "Nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN in .env)"}
    ok, msg = check_gateway()
    return {"ok": ok, "message": msg}


@router.post("/send")
def oc_send(body: SendBody):
    """Sendet eine Nachricht an einen OC-Agenten (ATLAS → OC)."""
    from src.network.openclaw_client import send_message_to_agent, is_configured

    if not is_configured():
        raise HTTPException(status_code=503, detail="OC-Kanal nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN)")
    ok, response_text = send_message_to_agent(
        body.text, agent_id=body.agent_id, user=body.user, timeout=60.0
    )
    if not ok:
        raise HTTPException(status_code=502, detail=response_text)
    return {"ok": True, "response": response_text}


@router.post("/fetch")
def oc_fetch():
    """Holt Einreichungen von OC (OC → ATLAS): liest rat_submissions vom VPS, speichert lokal."""
    from src.scripts.fetch_oc_submissions import run_fetch

    ok, count, items = run_fetch(dry_run=False)
    if not ok:
        raise HTTPException(status_code=502, detail="Fetch fehlgeschlagen (SSH oder Konfiguration)")
    return {"ok": True, "count": count, "items": items}


@router.get("/fetch")
def oc_fetch_get():
    """Wie POST /fetch – gleiche Aktion, GET für einfachen Aufruf."""
    from src.scripts.fetch_oc_submissions import run_fetch

    ok, count, items = run_fetch(dry_run=False)
    if not ok:
        raise HTTPException(status_code=502, detail="Fetch fehlgeschlagen (SSH oder Konfiguration)")
    return {"ok": True, "count": count, "items": items}


# Kurzfassung der WhatsApp-Plan-Aufgabe für OC (für trigger_whatsapp_plan)
_OC_WHATSAPP_PLAN_TASK = """Abstimmung WhatsApp-Plan: Bitte fülle Abschnitt 6 aus (Procedere allowFrom/getrennte Nummer, was du siehst). Antwort in rat_submissions mit topic "WhatsApp-Plan Abschnitt 6"."""


@router.post("/trigger_whatsapp_plan")
def oc_trigger_whatsapp_plan():
    """
    Löst die OC-Abstimmung zum WhatsApp-Plan aus (Logikketten-Workaround).

    Logik: Zuerst Versuch per API (send_message_to_agent). Bei Fehler (z. B. 405)
    Fallback: Task-Datei per SSH in OCs Workspace legen. Geeignet für HA-Logikschalter:
    Automation bei input_boolean oder Event → rest_command → dieses Endpoint.
    """
    import subprocess
    from src.network.openclaw_client import send_message_to_agent, is_configured

    # 1. Versuch: API
    if is_configured():
        ok, response_text = send_message_to_agent(
            _OC_WHATSAPP_PLAN_TASK,
            agent_id="main",
            timeout=30.0,
        )
        if ok:
            return {
                "ok": True,
                "method": "api",
                "message": "OC per API benachrichtigt.",
                "response_preview": (response_text[:200] + "...") if len(response_text or "") > 200 else response_text,
            }
        # 405 oder anderer Fehler → Fallback
        if "405" in response_text or "Method Not Allowed" in response_text:
            pass  # Fallback unten
        else:
            return {"ok": False, "method": "api", "message": response_text}

    # 2. Fallback: Task-Datei in Workspace legen (SSH)
    import os as _os
    _root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", ".."))
    try:
        result = subprocess.run(
            [__import__("sys").executable, "-m", "src.scripts.deploy_whatsapp_plan_task_to_oc"],
            cwd=_root,
            capture_output=True,
            text=True,
            timeout=25,
        )
        if result.returncode == 0:
            # Optional: Eine WhatsApp an deine Nummer senden (Handy klingelt, OC sieht sie wenn gleicher Account)
            _wa_msg = "@OC Lies workspace/whatsapp_plan_task.md und fülle Abschnitt 6 aus; Antwort in rat_submissions (topic: WhatsApp-Plan Abschnitt 6)."
            _target = _os.environ.get("WHATSAPP_TARGET_ID", "").strip().strip('"')
            _sent = False
            if _target and _os.environ.get("HASS_URL") and _os.environ.get("HASS_TOKEN"):
                try:
                    from src.network.ha_client import HAClient
                    _sent = HAClient().send_whatsapp(to_number=_target, text=_wa_msg)
                except Exception:
                    pass
            return {
                "ok": True,
                "method": "fallback_deploy",
                "message": "Task in Workspace gelegt. Eine WhatsApp mit @OC wurde" + (" an deine Nummer gesendet (Handy sollte klingeln; OC sieht sie)." if _sent else " nicht automatisch gesendet (HA/WHATSAPP_TARGET_ID prüfen). Du kannst sie manuell schicken: " + _wa_msg[:60] + "..."),
                "whatsapp_sent": _sent,
            }
    except Exception as e:
        return {"ok": False, "method": "fallback_deploy", "message": str(e)}
    return {"ok": False, "method": "fallback_deploy", "message": "Deploy-Skript fehlgeschlagen (SSH/VPS)."}
