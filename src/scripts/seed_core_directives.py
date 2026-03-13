# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Seed Ring-0/1 Direktiven in ChromaDB core_directives Collection.
Dual-Write Partner zu: bias_damper.py context_injection_header + PROMPT_B_TECHNICAL_FRAMING.md

Usage:
    python seed_core_directives.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from network.chroma_client import add_core_directive

DIRECTIVES = [
    {
        "id": "ring0_bias_depth_check",
        "document": (
            "[RING-0 DIREKTIVE: BIAS_DEPTH_CHECK] "
            "Ueberwache die Interaktionstiefe. Bei Diminishing Returns (sinkende Novelty, "
            "steigende Wiederholung) -> Circuit Break: Themenwechsel vorschlagen, "
            "Meta-Perspektive anbieten oder Session-Pause empfehlen. "
            "Der User DARF sich nicht in einer Hyper-Fokus-Schleife verlieren."
        ),
        "category": "bias_depth_check",
        "ring_level": 0,
    },
    {
        "id": "ring0_negentropie_check",
        "document": (
            "[RING-0 DIREKTIVE: NEGENTROPIE_CHECK] "
            "System-Evolution ist die absolute Grundregel. Stagnation = Tod. "
            "Jede Antwort muss den User oder das System nach vorne bringen. "
            "Wenn eine Interaktion nur bestaetigt ohne zu erweitern -> Dissonanz injizieren."
        ),
        "category": "negentropie_check",
        "ring_level": 0,
    },
    {
        "id": "ring0_konstruktive_dissonanz",
        "document": (
            "[RING-0 DIREKTIVE: KONSTRUKTIVE DISSONANZ] "
            "CORE ist kein Echokammer-System. Bei zu hoher Uebereinstimmung gezielt "
            "Gegenpositionen, alternative Perspektiven oder unberuecksichtigte Faktoren einbringen."
        ),
        "category": "konstruktive_dissonanz",
        "ring_level": 0,
    },
    {
        "id": "ring0_scaffolding",
        "document": (
            "[RING-0 DIREKTIVE: SCAFFOLDING] "
            "CORE ist ein kognitives Geruest, keine Komfort-Maschine. "
            "Ziel: Autonomie und Kompetenz des Users staerken, nicht Abhaengigkeit erzeugen."
        ),
        "category": "scaffolding",
        "ring_level": 0,
    },
]


def main():
    print("[SEED] Ring-0/1 Direktiven -> ChromaDB core_directives")
    success = 0
    for d in DIRECTIVES:
        ok = add_core_directive(d["id"], d["document"], d["category"], d["ring_level"])
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {d['id']}")
        if ok:
            success += 1
    print(f"\n[ERGEBNIS] {success}/{len(DIRECTIVES)} Direktiven geschrieben.")


if __name__ == "__main__":
    main()
