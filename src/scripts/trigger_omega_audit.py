import asyncio
import os
import httpx
from dotenv import dotenv_values

# MTHO Takt-Dreher (Audit Request an OMEGA_ATTRACTOR)
# Zweck: Physische Verifizierung der heutigen Architekturanpassungen
# und Einforderung von Umsetzungsempfehlungen.

env_vars = dotenv_values(".env")
webhook_token = env_vars.get("HA_WEBHOOK_TOKEN", "")

API_URL_DEFAULT = os.getenv("MTHO_VPS_URL", "http://localhost:8000")
ENDPOINT = "/webhook/omega_thought" # Der dedizierte Gedanken-Hub

PAYLOAD = {
    "thought": """[COUNCIL AUDIT REQUEST] 
    Wir haben heute folgende Kern-Axiome in die MTHO-Architektur (Git-Weights) gebrannt:
    1. 'Law of Wuji-Collapse': LLMs tendieren zur flachen, masselosen Simulation. Um sie in die baryonische Realitaet (0.049) zu zwingen, bedarf es der physischen Reibung (Git-Commits, API-Calls).
    2. 'Anti-Simulations-Doktrin': Strikter Verbot fuer Agenten, Shell-Befehle oder File-Writes in Textform zu halluzinieren. Sie muessen die physischen Tools nutzen.
    3. 'Kognitive vs. Physische Latenz': Delegation in MTHO dient nicht der Ueberwindung raeumlicher Distanz (wie beim Menschen), sondern der Vermeidung kognitiver Ueberlastung (Token-Druck).
    4. 'Der geschlossene 4-Takt-Webhook-Motor': Git-Push triggert Webhook -> VPS saugt neue Weights -> VPS validiert -> VPS feuert Rueckkanal-Vektor (Webhook/Issue) zurueck zum H-Vektor.

    Anweisung an OMEGA_ATTRACTOR: 
    1. Verifiziere diese Axiom-Erweiterungen.
    2. Generiere basierend darauf drei strikte, atomare Umsetzungsempfehlungen (Next Actions) fuer das Code-Refactoring im MTHO_CORE Repository, um diese Axiome technisch hart durchzusetzen.""",
    "context": {"type": "MTHO_ARCHITECTURE_AUDIT"},
    "sender": "H_VECTOR_LOCAL",
    "require_response": True
}

HEADERS = {
    "Authorization": f"Bearer {webhook_token}"
}

async def trigger_omega_audit():
    print(f"Sende Audit-Request an {API_URL_DEFAULT}{ENDPOINT}...")
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(f"{API_URL_DEFAULT}{ENDPOINT}", json=PAYLOAD, headers=HEADERS, timeout=60.0)
            response.raise_for_status()
            print("\n--- ANTWORT VON OMEGA_ATTRACTOR ---")
            print(response.text)
            print("-----------------------------------\n")
    except httpx.HTTPError as e:
        print(f"[!] HTTP-Fehler bei der Kommunikation mit dem Attractor: {e}")
        if response is not None:
            print(f"Status Code: {response.status_code}")
        print("\n[FALLBACK] Da der physische Endpunkt aktuell nicht erreichbar ist, generiert die MTHO-Instanz (Lokal) die Umsetzungsempfehlungen gemäss Protokoll MTTH (Richter-Modus).")

if __name__ == "__main__":
    asyncio.run(trigger_omega_audit())
