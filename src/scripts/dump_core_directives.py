# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
Dump aller core_directives aus ChromaDB (Ziel: .env CHROMA_*).
Für Vergleich Repo (Dreadnought) vs. VPS (OC Brain).
Ausgabe: JSON mit ids, documents, metadatas.
"""
import os
import sys
import json
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

def main():
    parser = argparse.ArgumentParser(description="Dump core_directives aus ChromaDB")
    parser.add_argument("--output", "-o", default=None, help="JSON-Datei (sonst stdout)")
    parser.add_argument("--summary", action="store_true", help="Nur IDs und Kategorien ausgeben")
    args = parser.parse_args()

    from src.network.chroma_client import get_core_directives_collection

    col = get_core_directives_collection()
    out = col.get(include=["documents", "metadatas"])
    payload = {
        "ids": out["ids"],
        "documents": out.get("documents") or [],
        "metadatas": out.get("metadatas") or [],
    }
    if args.summary:
        summary = [{"id": i, "category": (m or {}).get("category"), "ring": (m or {}).get("ring_level")} for i, m in zip(payload["ids"], payload["metadatas"])]
        text = json.dumps(summary, indent=2, ensure_ascii=False)
    else:
        text = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Geschrieben: {args.output} ({len(payload['ids'])} Einträge)")
    else:
        print(text)


if __name__ == "__main__":
    main()
