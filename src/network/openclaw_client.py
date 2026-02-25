"""
OpenClaw Gateway Client (Hostinger).
Liest VPS_HOST und OPENCLAW_GATEWAY_TOKEN aus .env.
Verknüpfung für spätere API-Calls an das OpenClaw-Gateway (z.B. Nachrichten senden/empfangen).
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

VPS_HOST = os.getenv("VPS_HOST", "")
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
# OpenClaw Gateway läuft typisch auf Port 18789 (laut Docs)
OPENCLAW_GATEWAY_PORT = int(os.getenv("OPENCLAW_GATEWAY_PORT", "18789"))


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


def check_gateway(timeout: float = 5.0) -> tuple[bool, str]:
    """
    Testet die Erreichbarkeit des OpenClaw-Gateways (GET auf Basis-URL).
    Returns: (success, message)
    """
    if not is_configured():
        return False, "Nicht konfiguriert (VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
    try:
        import requests
        url = gateway_url("/")
        r = requests.get(url, headers=auth_headers(), timeout=timeout)
        r.raise_for_status()
        return True, f"OK {r.status_code} – Gateway erreichbar"
    except requests.exceptions.Timeout:
        return False, "Timeout – Gateway nicht erreichbar"
    except requests.exceptions.ConnectionError as e:
        return False, f"Verbindungsfehler: {e}"
    except requests.exceptions.HTTPError as e:
        return False, f"HTTP {e.response.status_code}: {e}"
    except Exception as e:
        return False, f"Fehler: {e}"
