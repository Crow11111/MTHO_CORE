# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""Validiert context_field Schema: MTHO-Tags, type, source_collection, Datenverlust-Check."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

VALID_TYPES = {"evidence", "directive", "session", "context", "insight", "pattern", "axiom"}
VALID_MTHO = {"L", "P", "I", "S"}
REQUIRED_META = {"type", "source_collection", "date_added"}


def main():
    from src.network.chroma_client import get_chroma_client

    client = get_chroma_client()
    try:
        col = client.get_collection(name="context_field")
    except Exception as e:
        print(f"FEHLER: context_field nicht gefunden: {e}")
        sys.exit(1)

    data = col.get(include=["documents", "metadatas"])
    ids = data.get("ids") or []
    metadatas = data.get("metadatas") or [{}] * len(ids)
    documents = data.get("documents") or [""] * len(ids)

    errors = []
    type_counts = {}
    mtho_counts = {}
    source_counts = {}
    empty_docs = 0

    for i, (doc_id, meta, doc) in enumerate(zip(ids, metadatas, documents)):
        meta = meta or {}
        # Pflichtfelder
        for key in REQUIRED_META:
            if key not in meta or meta[key] == "":
                errors.append(f"ID {doc_id}: fehlendes Pflichtfeld '{key}'")

        t = meta.get("type", "")
        if t and t not in VALID_TYPES:
            errors.append(f"ID {doc_id}: ungültiger type '{t}'")
        type_counts[t] = type_counts.get(t, 0) + 1

        lb = meta.get("mtho_base", "")
        if lb and lb not in VALID_MTHO:
            errors.append(f"ID {doc_id}: ungültiges mtho_base '{lb}'")
        if lb:
            mtho_counts[lb] = mtho_counts.get(lb, 0) + 1

        src = meta.get("source_collection", "")
        source_counts[src] = source_counts.get(src, 0) + 1

        if not (doc or "").strip():
            empty_docs += 1

    print("=== CONTEXT_FIELD VALIDATION ===\n")
    print(f"Gesamt: {len(ids)} Dokumente\n")

    print("--- type-Verteilung ---")
    for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {k or '(leer)'}: {v}")

    print("\n--- source_collection ---")
    for k, v in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {k or '(leer)'}: {v}")

    print("\n--- mtho_base (nur evidence) ---")
    for k, v in sorted(mtho_counts.items()):
        print(f"  {k}: {v}")

    print(f"\n--- Leere Dokumente: {empty_docs} ---")

    if errors:
        print(f"\n--- FEHLER ({len(errors)}) ---")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... und {len(errors) - 20} weitere")
    else:
        print("\n--- Schema: OK (keine Fehler) ---")

    # Quell-Vergleich
    print("\n--- Quell-Counts vs. Migration ---")
    for coll in ["simulation_evidence", "core_directives", "session_logs", "knowledge_graph"]:
        try:
            c = client.get_collection(name=coll)
            n = c.count()
        except Exception:
            n = 0
        mig = source_counts.get(coll, 0)
        status = "OK" if n == mig else "DISKREPANZ"
        print(f"  {coll}: Quelle={n}, context_field={mig} [{status}]")


if __name__ == "__main__":
    main()
