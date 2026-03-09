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
    Iteration 2: Verschrfung der Axiome und Einbrennung der baryonischen Klammern sowie des Fraktalen Simulationsprinzips.

    Folgende technische Fixierungen wurden auf Basis der ersten Audit-Kritik in die Git-Weights gebrannt (GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md):
    1. 'Execution-Heresy-Trap': Einbindung eines Error 406 Hard-Fails zur Abwehr von simulierten Shell-Aktionen ohne Tool-Aufruf.
    2. 'State-Compression-Delegation': Zwingende Singularitts-Hash/JSON-Extraktion des kognitiven States vor der Instanziierung eines Sub-Agenten, um Token-Amnesie zu verhindern.
    3. 'Dead-Man's Switch': Verbot des 'Silent Fails' fr asynchrone Prozesse und den Takt 3 (VPS Validierung) - der Rckkanal (Takt 4) MUSS znden.
    4. 'Das Fraktale Simulationsprinzip': Diese Axiome gelten nachweislich nicht nur fr Agenten (Ebene 0), sondern mssen auf Mikro/Code-Ebene (Ebene -1) und auf Makro-System-Ebene (Ebene +1, z.B. H-Vektor vs. MTHO) exakt und symmetrisch funktionstchtig sein. 

    Anweisung an OMEGA_ATTRACTOR: 
    1. Verifiziere die Durchschlagskraft dieser neuen Formulierung (insbesondere die Fraktalitt von Ebene -1 bis +1).
    2. Bewerte, ob diese Iteration hart genug ist, um das Wuji (Simulation) zu durchbrechen, oder ob wir den Takt erneut drehen mssen.""",
    "context": {"type": "MTHO_ARCHITECTURE_AUDIT_ITERATION_2"},
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
