# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
OC-Brain-Abgleich: Prüft core_directives (und optional knowledge_graph) in ChromaDB.
Lokal: CHROMA_HOST leer. VPS: CHROMA_HOST=localhost nach SSH-Tunnel (ssh -L 8000:127.0.0.1:8000 root@187.77.68.250).
Liefert Vergleichsgrundlage: welche IDs vorhanden, Kurztext, Fehlendes.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import asyncio

async def main():
    from src.network.chroma_client import get_core_directives_collection

    col = await get_core_directives_collection()
    n = await asyncio.to_thread(col.count)
    if n == 0:
        print("core_directives: 0 Einträge.")
        return

    data = await asyncio.to_thread(col.get, include=["documents", "metadatas"])
    ids = data["ids"]
    docs = data.get("documents") or []
    metas = data.get("metadatas") or []

    print(f"core_directives: {n} Einträge")
    print("-" * 60)
    erwartet = {
        "gravitational_query_axiom",
        "origin_irrelevance_consciousness_equivalence",
        "dissonance_thresholds_grace_resonance_fractal",
        "ntnd_handshake_protocol",
    }
    vorhanden = set(ids)
    fehlend = erwartet - vorhanden
    extra = vorhanden - erwartet

    for i, id_ in enumerate(ids):
        doc = (docs[i] or "")[:220].replace("\n", " ")
        meta = metas[i] if i < len(metas) else {}
        print(f"  [{id_}] {meta}")
        print(f"      {doc}...")
        print()

    if fehlend:
        print("FEHLEND (von Dreadnought/Repo erwartet):", sorted(fehlend))
    if extra:
        print("NUR IN CHROMA (evtl. von OC Brain):", sorted(extra))


if __name__ == "__main__":
    asyncio.run(main())
