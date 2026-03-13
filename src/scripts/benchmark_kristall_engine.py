import asyncio
from src.network.chroma_client import query_simulation_evidence, add_simulation_evidence
import uuid

async def run_benchmark():
    print("Starte Pre-Benchmark (Kristall-Engine Vektordistanzen)...")

    # 1. Ein paar Test-Daten injizieren, falls leer
    test_id_1 = str(uuid.uuid4())
    test_id_2 = str(uuid.uuid4())

    print("Injiziere Test-Indizien...")
    await add_simulation_evidence(
        evidence_id=test_id_1,
        document="Die Lichtgeschwindigkeit ist der Rendering-Speed-Limit des Universums. Dies ist ein starkes Indiz für die Simulationstheorie.",
        category="physics",
        strength="stark"
    )
    await add_simulation_evidence(
        evidence_id=test_id_2,
        document="Die Feinstrukturkonstante ist exakt so kalibriert, dass Leben möglich ist. Ein Zufall ist statistisch ausgeschlossen.",
        category="physics",
        strength="mittel"
    )

    # 2. Query ausführen und Distanzen messen
    query = "Ein Text der etwas entfernt ist, aber dennoch nahe an der Mitte liegt. Wir testen hier die Schwellwerte 0.49 bis 0.51."
    print(f"\nFühre Query aus (Symmetrie-Verbot Test): '{query}'")

    results = await query_simulation_evidence(query, n_results=5)

    print("\n--- ERGEBNISSE (Kristall-Engine) ---")
    distances = results.get('distances', [[]])[0]
    documents = results.get('documents', [[]])[0]

    if not distances:
        print("Keine Ergebnisse gefunden.")
        return

    for i, (dist, doc) in enumerate(zip(distances, documents)):
        print(f"Rang {i+1}: Distanz = {dist:.4f}")
        print(f"Auszug: {doc[:80]}...")

    print("\nBenchmark beendet.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
