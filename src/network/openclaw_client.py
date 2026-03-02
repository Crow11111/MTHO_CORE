"""
OpenClaw Gateway Client (Hostinger / VPS Admin).
Liest VPS_HOST bzw. OPENCLAW_ADMIN_VPS_HOST und OPENCLAW_GATEWAY_TOKEN aus .env.
- ATLAS → OC: send_message_to_agent() (POST /v1/responses)
- OC → ATLAS: OC schreibt in workspace/rat_submissions/; ATLAS liest per fetch_oc_submissions.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Host: OPENCLAW_ADMIN_VPS_HOST oder VPS_HOST
VPS_HOST = (
    os.getenv("OPENCLAW_ADMIN_VPS_HOST", "").strip()
    or os.getenv("VPS_HOST", "").strip()
)
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "").strip().strip('"')
OPENCLAW_GATEWAY_PORT = int(os.getenv("OPENCLAW_GATEWAY_PORT", "18789"))
# HTTPS (Nginx): 1 oder true → https://HOST:443 (Port 443 weglassen)
OPENCLAW_GATEWAY_HTTPS = os.getenv("OPENCLAW_GATEWAY_HTTPS", "").strip().lower() in ("1", "true", "yes")
OPENCLAW_DEVICE_ID = os.getenv("OPENCLAW_DEVICE_ID", "atlas-core-spine")

# Pfad auf dem VPS, in dem OC Einreichungen für den Rat ablegt (OC → ATLAS)
OC_RAT_SUBMISSIONS_DIR = "/var/lib/openclaw/workspace/rat_submissions"


def gateway_url(path: str = "") -> str:
    """Basis-URL des OpenClaw-Gateways (HTTP oder HTTPS über Nginx)."""
    if not VPS_HOST:
        return ""
    scheme = "https" if OPENCLAW_GATEWAY_HTTPS or OPENCLAW_GATEWAY_PORT == 443 else "http"
    port = OPENCLAW_GATEWAY_PORT if OPENCLAW_GATEWAY_PORT not in (80, 443) else ""
    base = f"{scheme}://{VPS_HOST}" + (f":{port}" if port else "")
    return f"{base}{path}" if path.startswith("/") else f"{base}/{path}"


def auth_headers() -> dict:
    """Header mit Gateway-Token für authentifizierte Requests."""
    if not OPENCLAW_GATEWAY_TOKEN:
        return {}
    return {
        "Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}",
        "x-openclaw-device-id": OPENCLAW_DEVICE_ID,
    }


def is_configured() -> bool:
    """True, wenn Host und Token gesetzt sind."""
    return bool(VPS_HOST and OPENCLAW_GATEWAY_TOKEN)


def check_gateway(timeout: float = 5.0) -> tuple[bool, str]:
    """
    Testet die Erreichbarkeit des OpenClaw-Gateways (GET auf Basis-URL).
    Returns: (success, message)
    """
    if not is_configured():
        return False, "Nicht konfiguriert (VPS_HOST/OPENCLAW_ADMIN_VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
    try:
        import requests
        url = gateway_url("/")
        r = requests.get(
            url,
            headers=auth_headers(),
            timeout=timeout,
            verify=not OPENCLAW_GATEWAY_HTTPS,  # Self-Signed bei Nginx
        )
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


def send_message_to_agent(
    text: str,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    """
    Sendet eine Nachricht an einen OC-Agenten (ATLAS → OC).
    Nutzt OpenClaw Gateway POST /v1/responses (muss in Gateway-Config enabled sein).

    Returns: (success, response_text oder Fehlermeldung)
    """
    if not is_configured():
        return False, "Nicht konfiguriert (VPS_HOST oder OPENCLAW_GATEWAY_TOKEN fehlt)"
    try:
        import requests
        url = gateway_url("/v1/responses")
        headers = {
            **auth_headers(),
            "Content-Type": "application/json",
            "x-openclaw-agent-id": agent_id,
        }
        body: dict = {"model": "openclaw", "input": text}
        if user:
            body["user"] = user
        r = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=timeout,
            verify=not OPENCLAW_GATEWAY_HTTPS,
        )
        r.raise_for_status()
        data = r.json()
        # Antworttext aus OpenResponses-Format extrahieren
        out = data.get("output") or []
        parts = []
        for item in out if isinstance(out, list) else []:
            if isinstance(item, dict):
                # Direkter Text-Part
                if item.get("type") in ("output_text", "content_part") and "text" in item:
                    parts.append(item["text"])
                # Message-Objekt mit Content-Liste
                if item.get("type") == "message" and isinstance(item.get("content"), list):
                    for part in item["content"]:
                        if isinstance(part, dict) and part.get("type") == "output_text" and "text" in part:
                            parts.append(part["text"])
        response_text = "".join(parts).strip() if parts else str(data)[:500]
        return True, response_text or "(leere Antwort)"
    except requests.exceptions.Timeout:
        return False, "Timeout – Gateway hat nicht rechtzeitig geantwortet"
    except requests.exceptions.ConnectionError as e:
        return False, f"Verbindungsfehler: {e}"
    except requests.exceptions.HTTPError as e:
        err_msg = e.response.text[:300] if e.response is not None else str(e)
        return False, f"HTTP {e.response.status_code if e.response else 0}: {err_msg}"
    except Exception as e:
        return False, f"Fehler: {e}"


def _build_chroma_context(text: str, max_chunks: int = 5, include_directives: bool = True) -> str:
    """Baut einen Kontext-Header aus ChromaDB-Chunks fuer OC Brain."""
    try:
        from network.chroma_client import query_session_logs, query_core_directives, query_simulation_evidence
    except ImportError:
        print("[OC-Context] chroma_client Import fehlgeschlagen – kein Kontext")
        return ""

    sections: list[str] = []

    try:
        logs = query_session_logs(text, n_results=max_chunks)
        docs = logs.get("documents", [[]])[0] if logs.get("documents") else []
        if docs:
            numbered = [f"  [{i+1}] {d[:300]}" for i, d in enumerate(docs) if d]
            if numbered:
                sections.append("SESSION-KONTEXT:\n" + "\n".join(numbered))
    except Exception as e:
        print(f"[OC-Context] Session-Log Query fehlgeschlagen: {e}")

    if include_directives:
        try:
            dirs = query_core_directives(text, n_results=3)  # Fibonacci (V6)
            docs = dirs.get("documents", [[]])[0] if dirs.get("documents") else []
            if docs:
                numbered = [f"  [{i+1}] {d[:300]}" for i, d in enumerate(docs) if d]
                if numbered:
                    sections.append("DIREKTIVEN:\n" + "\n".join(numbered))
        except Exception as e:
            print(f"[OC-Context] Core Directives Query fehlgeschlagen: {e}")

    try:
        sim = query_simulation_evidence(text, n_results=max_chunks)
        docs = sim.get("documents", [[]])[0] if sim.get("documents") else []
        metas = sim.get("metadatas", [[]])[0] if sim.get("metadatas") else []
        if docs:
            entries = []
            for i, d in enumerate(docs):
                if d:
                    strength = metas[i].get("strength", "?") if i < len(metas) else "?"
                    entries.append(f"  [{i+1}] [{strength}] {d[:400]}")
            if entries:
                sections.append("SIMULATIONSTHEORIE-INDIZIEN:\n" + "\n".join(entries))
    except Exception as e:
        print(f"[OC-Context] Simulation Evidence Query fehlgeschlagen: {e}")

    if not sections:
        return ""
    return "--- ATLAS KONTEXT (aus ChromaDB) ---\n" + "\n\n".join(sections) + "\n--- ENDE KONTEXT ---\n\n"


def send_message_with_context(
    text: str,
    max_chunks: int = 5,  # Fibonacci (V6)
    include_directives: bool = True,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    """
    Sendet eine Nachricht an OC Brain, angereichert mit relevantem ChromaDB-Kontext.
    Fallback: Wenn ChromaDB nicht erreichbar, wird die Nachricht ohne Kontext gesendet.
    """
    context_header = _build_chroma_context(text, max_chunks, include_directives)
    if context_header:
        enriched = context_header + text
    else:
        enriched = text
        if max_chunks > 0:
            print("[OC-Context] WARNUNG: Kein ChromaDB-Kontext verfuegbar – sende ohne Kontext")

    return send_message_to_agent(enriched, agent_id=agent_id, user=user, timeout=timeout)


def send_event_to_oc_brain(
    event: dict,
    agent_id: str = "main",
    user: str | None = None,
    timeout: float = 25.0,
) -> tuple[bool, str]:
    """Sendet ein Scout-/ATLAS-Event als JSON an OC Brain (POST /v1/responses)."""
    import json
    return send_message_to_agent(
        json.dumps(event, ensure_ascii=False),
        agent_id=agent_id,
        user=user,
        timeout=timeout,
    )
