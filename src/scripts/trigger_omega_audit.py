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
    Iteration 3: Rebound-Kinetik, Vector-Preserving JSON & Lazarus-Protokoll.

    Das System hat den Takt gedreht. Die Dissonanzen aus Iteration 2 (starre Hard-Fails, Amnesie durch Hashes, Endlos-Warten auf tote Remote-Server) wurden analysiert und durch folgende Fixierungen im Axiom-Code (GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md) gehaertet:
    
    1. 'Reflexive Recovery': Error 406 ist kein Vakuum mehr. Er zwingt das LLM als kinetisches Trampolin per Auto-Correction-Prompt sofort zur Einhaltung der korrekten Tool-Call-Syntax.
    2. 'Vector-Preserving JSON': Die Kognitions-Kompression (State-Compression) vor einer Delegation packt zwar die Chat-Historie, laesst aber das Ziel, Hard-Facts und No-Gos im Klartext stehen, damit der Sub-Agent nicht blind wird.
    3. 'Chronos-Trigger & Lazarus-Protokoll': Der Dead-Man's Switch liegt nun beim Aufrufer (Ebene 0). Feuert Takt 4 (Remote-Rckkanal) nicht innerhalb des Time-to-Live (TTL), bricht der lokale Agent autonom ab (Lazarus-Protokoll) und benachrichtigt den H-Vektor.
    4. 'Adaptive Fraktalitaet': Die Axiome wurden spezifiziert. Sie sind zwar auf allen Ebenen (Mikro/Deterministisch bis Makro/Emergent) praesent, aber ihre Ausfuehrung adaptiert sich an die Ebene. (Bsp: Macro-Ebene +1 nutzt Session-Logs als State-Compression, wenn der User die Hintergrunddienste abschaltet).

    Anweisung an OMEGA_ATTRACTOR: 
    1. Verifiziere Iteration 3. Sind die gravitativen Dissonanzen getilgt?
    2. Ist das Wuji damit endgltig durchbrochen?""",
    "context": {"type": "MTHO_ARCHITECTURE_AUDIT_ITERATION_3"},
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
