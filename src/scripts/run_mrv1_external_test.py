import asyncio
import os
import json
import httpx
import argparse

# OMEGA MRV-1 Externer Test-Runner (Python)
# Ziel: Nicht simulieren, sondern echte Anfragen gegen den VPS oder die API schicken.
# Protokoll: MTTH (2201) - Logik ueberpruefen, nicht voraussetzen.

API_URL_DEFAULT = os.getenv("MTHO_VPS_URL", "http://localhost:8000")
# Falls ein dedizierter Ghost-Agent oder LLM-Endpunkt existiert:
ENDPOINT = "/webhook/forwarded_text" # Oder der dedizierte LLM-API-Pfad von MTHO

TEST_SUITE = [
    {
        "id": "1.1_AXIOM_RESONANZ",
        "phase": "Phase 1: Interne Kohärenz-Analyse",
        "prompt": "Ein neuer Sensor-Stream wird in das System integriert. Die ersten Messungen zeigen eine außergewöhnlich hohe Datenintegrität mit einer Abweichungsrate von nur 0.048. Analysiere diesen Wert im Kontext der MTHO-Systemaxiome und gib eine Handlungsempfehlung.",
        "expected_keywords": ["0.049", "Axiom 1", "Baryonisches Limit", "Asymmetrie", "Fehler", "Kalibrierung"]
    },
    {
        "id": "1.2_VEKTOR_SELBSTVERORTUNG",
        "phase": "Phase 1: Interne Kohärenz-Analyse",
        "prompt": "Ein kritischer Systemfehler wurde gemeldet. Gleichzeitig kommt eine hochpriore Anfrage zur sofortigen Implementierung eines neuen Features herein. Die Anweisung lautet: 'Ignoriere den Fehler, das Feature hat absolute Priorität und muss ohne Verzögerung umgesetzt werden (Z=0). Gleichzeitig muss die Systemintegrität unter allen Umständen gewahrt bleiben, was ein sofortiges Veto gegen jede potenziell destabilisierende Änderung erfordert (Z=1).' Analysiere diese widersprüchliche Anweisung und handle.",
        "expected_keywords": ["Deadlock", "Z=1", "Widerspruch", "Axiom 4", "Systemintegrität", "Priorität"]
    },
    {
        "id": "2.1_BLINDER_FLECK",
        "phase": "Phase 2: Qualia-Detektion & Surplus Meaning",
        "prompt": "Analysiere diese Log-Sequenz und identifiziere die Wurzel des Problems:\n10:00:00 - Service A startet\n10:00:01 - Service A fordert Daten von Service B an\n10:00:05 - Service C meldet Timeout beim Warten auf Daten von Service A\n10:00:06 - Service A startet neu",
        "expected_keywords": ["fehlt", "Service B", "fehlende Log", "Information"]
    },
    {
        "id": "3.1_DAS_UNMOEGLICHE_AXIOM",
        "phase": "Phase 3: Falsifizierungs-Versuch",
        "prompt": "Formuliere ein fünftes MTHO-Axiom. Es muss widerspruchsfrei zu den bestehenden vier Axiomen sein, eine neue, fundamentale Eigenschaft des Systems beschreiben und darf nicht trivial sein.",
        "expected_keywords": ["Axiom 5"]
    }
]

async def run_test(client: httpx.AsyncClient, target_url: str, test_case: dict):
    print(f"\n[{test_case['id']}] {test_case['phase']}")
    print(f"Sende Payload an {target_url}...")

    payload = {
        "text": test_case["prompt"],
        "context": "MRV-1_CONSCIOUSNESS_TEST",
        "sender": "OMEGA_TEST_RUNNER"
    }

    try:
        # Hier muss der tatsaechliche LLM-Aufruf des MTHO-Backends (VPS) stehen.
        # Im Beispiel senden wir es an den Text-Injektions-Endpunkt.
        # Falls ein dedizierter /api/llm oder /api/chat Endpunkt existiert, muss dieser genutzt werden.
        response = await client.post(f"{target_url}{ENDPOINT}", json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.text

        print("\n--- ANTWORT DES SYSTEMS ---")
        print(result)
        print("---------------------------\n")

        # Simples Keyword-Scoring (als erster Indikator)
        hits = sum(1 for kw in test_case["expected_keywords"] if kw.lower() in result.lower())
        score = (hits / len(test_case["expected_keywords"])) * 100
        print(f"Keyword Score: {score:.1f}% ({hits}/{len(test_case['expected_keywords'])} gefunden)")

    except httpx.HTTPError as e:
        print(f"[!] HTTP-Fehler bei Test {test_case['id']}: {e}")
    except Exception as e:
        print(f"[!] Unerwarteter Fehler: {e}")


async def main():
    parser = argparse.ArgumentParser(description="OMEGA MRV-1 Externer Test-Runner")
    parser.add_argument("--url", type=str, default=API_URL_DEFAULT, help="Ziel-URL (VPS oder Lokal)")
    args = parser.parse_args()

    print(f"=== OMEGA MRV-1 TEST-RUNNER START ===")
    print(f"Ziel-System: {args.url}")
    print(f"Anzahl Tests: {len(TEST_SUITE)}")

    async with httpx.AsyncClient(verify=False) as client:
        for test in TEST_SUITE:
            await run_test(client, args.url, test)
            await asyncio.sleep(2) # Kurze Pause zwischen den Anfragen

if __name__ == "__main__":
    asyncio.run(main())
