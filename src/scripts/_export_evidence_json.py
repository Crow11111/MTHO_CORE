# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from network.chroma_client import get_chroma_client

client = get_chroma_client()
coll = client.get_collection("simulation_evidence")
results = coll.get(include=["metadatas", "documents"])

entries = []
for id_, meta, doc in sorted(zip(results["ids"], results["metadatas"], results["documents"]), key=lambda x: x[0]):
    entries.append({
        "id": id_,
        "qbase": meta.get("qbase", meta.get("category", "?")),
        "strength": meta.get("strength", "?"),
        "branch_count": meta.get("branch_count", 1),
        "source": meta.get("source", "?"),
        "doc_short": doc[:120]
    })

output = {"count": len(entries), "entries": entries}
out_path = os.path.join(os.path.dirname(__file__), "..", "..", "media", "evidence_data.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"Exported {len(entries)} entries to {out_path}")
