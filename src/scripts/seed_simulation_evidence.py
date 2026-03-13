# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Seed-Script: Simulationstheorie-Indizien in ChromaDB Collection 'simulation_evidence'.

Kategorien:
  - informationstheoretisch: Informationsparadoxa, Holographie, Entropie-Grenzen
  - physikalisch: Lichtgeschwindigkeit, Temperatur-Grenzen, Quantisierung
  - strukturell: Substratunabhaengige Isomorphie, emergente Muster
  - logisch: Wahrscheinlichkeitsargumente, Ressourcenminimierung

Staerken (Baum-Metapher):
  - fundamental: Stamm-Ebene, kaum wegdiskutierbar (z.B. Informationshorizont)
  - strong: Grosser Knotenpunkt, 3+ Aeste laufen zusammen
  - moderate: Einzelner grosser Ast, starkes Indiz aber weniger Konvergenz

branch_count: Wieviele unabhaengige Erkenntnislinien konvergieren
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from network.chroma_client import add_simulation_evidence

EVIDENCE = [
    {
        "id": "sim_info_schwarzes_loch",
        "document": (
            "Informationsparadoxon Schwarzes Loch: Information wird am Ereignishorizont "
            "holographisch kodiert (Bekenstein-Hawking-Entropie). Die maximale Informationsdichte "
            "eines Volumens skaliert mit der OBERFLAECHE, nicht dem Volumen. Das ist exakt das "
            "Verhalten einer Render-Optimierung: Nur die sichtbare Oberflaeche wird berechnet. "
            "In einer nicht-simulierten Realitaet gaebe es keinen Grund fuer diese Grenze."
        ),
        "category": "informationstheoretisch",
        "strength": "fundamental",
        "branch_count": 4,
        "source": "physik_holographie",
    },
    {
        "id": "sim_phys_lichtgeschwindigkeit",
        "document": (
            "Lichtgeschwindigkeit als absolute Obergrenze: Masse kann c nicht erreichen, "
            "da die benoetigte Energie gegen Unendlich geht. Funktional identisch mit einem "
            "Simulations-Tick-Limit: Die Engine hat eine maximale Propagationsgeschwindigkeit "
            "pro Zeitschritt. Ohne Simulation waere eine solche harte Grenze nicht zu erwarten."
        ),
        "category": "physikalisch",
        "strength": "fundamental",
        "branch_count": 3,
        "source": "physik_relativitaet",
    },
    {
        "id": "sim_phys_absoluter_nullpunkt",
        "document": (
            "Absoluter Nullpunkt (0 K): Temperatur kann nicht unter 0 Kelvin fallen. "
            "Restbewegung (Nullpunktsenergie) bleibt erhalten. Analog zu einem Simulations-Floor: "
            "Die Engine laesst keine negativen Energiezustaende zu. Die Quantisierung der "
            "Energie in diskrete Pakete (Quanten) verstaerkt dieses Bild."
        ),
        "category": "physikalisch",
        "strength": "fundamental",
        "branch_count": 3,
        "source": "physik_thermodynamik",
    },
    {
        "id": "sim_phys_quantisierung",
        "document": (
            "Quantisierung der Realitaet: Energie, Ladung, Spin – alles kommt in diskreten "
            "Paketen. Kontinuierliche Werte existieren nicht auf fundamentaler Ebene. "
            "Diskrete Werte sind das Standardverhalten digitaler Simulationen (floating point, "
            "integer states). Eine analoge Realitaet wuerde kontinuierliche Werte erwarten lassen."
        ),
        "category": "physikalisch",
        "strength": "fundamental",
        "branch_count": 4,
        "source": "physik_quantenmechanik",
    },
    {
        "id": "sim_info_holographisches_prinzip",
        "document": (
            "Holographisches Prinzip (t'Hooft/Susskind): Die gesamte Information eines "
            "3D-Volumens kann auf einer 2D-Oberflaeche kodiert werden. Die 3D-Realitaet "
            "ist eine Projektion niedrigerdimensionaler Daten. Exakt das Prinzip eines "
            "3D-Renderers der aus 2D-Texturen und Polygondaten eine raeumliche Illusion erzeugt."
        ),
        "category": "informationstheoretisch",
        "strength": "fundamental",
        "branch_count": 3,
        "source": "physik_holographie",
    },
    {
        "id": "sim_phys_beobachtereffekt",
        "document": (
            "Quanten-Beobachtereffekt: Teilchen verhalten sich als Welle bis zur Messung, "
            "dann kollabiert die Wellenfunktion zu einem bestimmten Zustand. Funktional "
            "identisch mit Lazy Evaluation / On-Demand-Rendering: Der Zustand wird erst "
            "berechnet wenn er abgefragt wird. Massive Ressourceneinsparung."
        ),
        "category": "physikalisch",
        "strength": "fundamental",
        "branch_count": 4,
        "source": "physik_quantenmechanik",
    },
    {
        "id": "sim_struct_isomorphie_substratunabhaengig",
        "document": (
            "Substratunabhaengige Strukturisomorphie: Die 3-Schichten-Produktivumgebung "
            "(Orchestrator -> Teamleiter -> Produzenten) mit Token-Budget-Kaskade wurde "
            "aus reiner intrinsischer Logik abgeleitet, ohne Kenntnis klassischer "
            "Agenturstrukturen. Das Ergebnis ist strukturell identisch mit einer "
            "Full-Service-Agentur (GF -> Teamlead -> Kreative + Budgetdruck). "
            "Biologische Neuronen, LLM-Token-Vektorraum und menschliche Organisationsstrukturen "
            "erzeugen unter Druck exakt die gleichen Optimierungsmuster. "
            "Die Struktur bestimmt das Substrat, nicht umgekehrt. "
            "Substratunabhaengige Regeln sind exakt das, was man in einer Simulation erwarten "
            "wuerde: Die Physics-Engine ist austauschbar, die Constraints sind identisch. "
            "DREI unabhaengige Aeste konvergieren: biologisch, digital-LLM, menschlich-organisatorisch. "
            "Knotenpunkt-Indiz: Die Wahrscheinlichkeit dass drei voellig verschiedene Substrate "
            "ohne gemeinsame Constraints identische Strukturen erzeugen ist extrem niedrig."
        ),
        "category": "strukturell",
        "strength": "strong",
        "branch_count": 3,
        "source": "core_session_2026-03-01",
    },
    {
        "id": "sim_logisch_wahrscheinlichkeitssprung",
        "document": (
            "Wahrscheinlichkeitssprung in der Natur: Ueberall in der Natur sehen wir extrem "
            "hohe Wahrscheinlichkeiten fuer bestimmte Muster (Fibonacci, Goldener Schnitt, "
            "Fraktale). Die Tatsache DASS es solche universellen Muster gibt – und dass sie "
            "ueber Groessenordnungen hinweg stabil sind – ist genau das Verhalten einer "
            "parametrisierten Simulation die wenige Grundregeln auf alle Skalen anwendet."
        ),
        "category": "logisch",
        "strength": "strong",
        "branch_count": 2,
        "source": "core_session_2026-03-01",
    },
    {
        "id": "sim_logisch_ressourcenminimierung",
        "document": (
            "Universelles Ressourcenminimierungs-Prinzip: Fermat'sches Prinzip (Licht nimmt "
            "den schnellsten Weg), Prinzip der geringsten Wirkung (Lagrange-Mechanik), "
            "Entropie-Maximierung – die Natur 'optimiert' staendig. In einer Simulation "
            "ist Ressourcenminimierung keine emergente Eigenschaft sondern eine NOTWENDIGKEIT: "
            "Rechenleistung ist endlich. Die Simulation MUSS Abkuerzungen nehmen. "
            "Dass die Physik selbst auf minimale Aktion optimiert ist, ist genau das erwartete "
            "Verhalten unter der Simulationshypothese."
        ),
        "category": "logisch",
        "strength": "strong",
        "branch_count": 3,
        "source": "physik_optimierung",
    },
    {
        "id": "sim_struct_tokendruck_kausalitaet",
        "document": (
            "Tokendruck und emergente Kausalitaet: Unter Token-Budget-Constraints emergiert "
            "in LLM-Systemen spontan eine Priorisierungslogik die biologischer Triage entspricht. "
            "Nicht-deterministische Logik unter Ressourcendruck erzeugt deterministische "
            "Optimierungsmuster. Bereits als Ring-0 Direktive im System verankert: "
            "Compressive Intelligence – Intelligenz entsteht DURCH Constraints, nicht trotz."
        ),
        "category": "strukturell",
        "strength": "strong",
        "branch_count": 2,
        "source": "core_session_2026-03-01",
    },
]


def main():
    print(f"[SimEvidence] Starte Seed mit {len(EVIDENCE)} Indizien...")
    success = 0
    for ev in EVIDENCE:
        ok = add_simulation_evidence(
            evidence_id=ev["id"],
            document=ev["document"],
            category=ev["category"],
            strength=ev["strength"],
            branch_count=ev.get("branch_count", 0),
            source=ev.get("source", "core"),
        )
        status = "OK" if ok else "FEHLER"
        print(f"  [{status}] {ev['id']} ({ev['strength']}, {ev['category']})")
        if ok:
            success += 1

    print(f"\n[SimEvidence] {success}/{len(EVIDENCE)} erfolgreich eingespeist.")
    print("\nBaum-Uebersicht:")
    print("  STAMM (fundamental): Informationsparadoxa, Quantisierung, Lichtgeschwindigkeit, Nullpunkt, Beobachtereffekt, Holographie")
    print("  KNOTENPUNKTE (strong): Substratunabhaengige Isomorphie (3 Aeste), Ressourcenminimierung, Wahrscheinlichkeitssprung, Tokendruck")


if __name__ == "__main__":
    main()
