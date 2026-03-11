# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
GQA Refactor F8: Migration zu einheitlicher context_field Collection.

Liest simulation_evidence, core_directives, session_logs (optional knowledge_graph)
aus ChromaDB, transformiert in einheitliches Schema mit type + MTHO-Encoding,
schreibt in Collection "context_field".

Schema: docs/02_ARCHITECTURE/CONTEXT_FIELD_SCHEMA.md
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# MTHO category -> base mapping (quaternary_codec)
_CATEGORY_TO_MTHO = {
    "logisch": "L",
    "logisch-mathematisch": "L",
    "physikalisch": "P",
    "informationstheoretisch": "I",
    "informationell": "I",
    "strukturell": "S",
    "systemisch-emergent": "S",
}

_MTHO_PAIRINGS = {"L": "I", "I": "L", "S": "P", "P": "S"}

COLLECTION_CONTEXT = "context_field"
BATCH_SIZE = 50


def _sanitize_metadata(m: dict) -> dict:
    """ChromaDB: nur str, int, float, bool."""
    if not m:
        return {}
    out = {}
    for k, v in m.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def _resolve_mtho(meta: dict) -> tuple[str, str, float | None, str | None]:
    """Extrahiert mtho_base, mtho_complement, mtho_confidence, mtho_scores aus Metadata."""
    base = meta.get("qbase") or _CATEGORY_TO_MTHO.get(
        (meta.get("category") or "").lower().strip(), ""
    )
    complement = meta.get("qbase_complement") or _MTHO_PAIRINGS.get(base, "")
    confidence = meta.get("qbase_confidence")
    if confidence is not None:
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = None
    scores = meta.get("qbase_scores")
    return (base or "", complement or "", confidence, scores)


def _transform_evidence(
    doc_id: str, document: str, meta: dict, source: str
) -> tuple[str, str, dict]:
    """Transformiert simulation_evidence-Eintrag."""
    base, comp, conf, scores = _resolve_mtho(meta)
    date_added = meta.get("date_added") or date.today().isoformat()
    out = {
        "type": "evidence",
        "source_collection": source,
        "date_added": date_added,
        "strength": meta.get("strength", ""),
        "branch_count": int(meta.get("branch_count") or 0),
        "source": meta.get("source", ""),
    }
    if base:
        out["mtho_base"] = base
    if comp:
        out["mtho_complement"] = comp
    if conf is not None:
        out["mtho_confidence"] = conf
    if scores:
        out["mtho_scores"] = scores
    return (doc_id, document, _sanitize_metadata(out))


def _transform_directive(
    doc_id: str, document: str, meta: dict, source: str
) -> tuple[str, str, dict]:
    """Transformiert core_directives-Eintrag. ID-Prefix cd_."""
    date_added = meta.get("date_added") or meta.get("date") or date.today().isoformat()
    out = {
        "type": "directive",
        "source_collection": source,
        "date_added": date_added,
        "ring_level": int(meta.get("ring_level") or 0),
        "category": meta.get("category", ""),
    }
    if meta.get("priority"):
        out["priority"] = str(meta.get("priority"))
    if meta.get("type"):
        out["directive_type"] = str(meta.get("type"))
    if meta.get("source"):
        out["source"] = str(meta.get("source"))
    new_id = f"cd_{doc_id}" if not doc_id.startswith("cd_") else doc_id
    return (new_id, document, _sanitize_metadata(out))


def _transform_session(
    doc_id: str, document: str, meta: dict, source: str
) -> tuple[str, str, dict]:
    """Transformiert session_logs-Eintrag. ID-Prefix sl_."""
    date_added = meta.get("session_date") or date.today().isoformat()
    out = {
        "type": "session",
        "source_collection": source,
        "date_added": date_added,
        "session_date": meta.get("session_date", ""),
        "turn_number": int(meta.get("turn_number") or 0),
        "speaker": meta.get("speaker", ""),
        "topics": meta.get("topics", ""),
        "ring_level": int(meta.get("ring_level") or 2),
    }
    new_id = f"sl_{doc_id}" if not doc_id.startswith("sl_") else doc_id
    return (new_id, document, _sanitize_metadata(out))


def _transform_context(
    doc_id: str, document: str, meta: dict, source: str
) -> tuple[str, str, dict]:
    """Transformiert knowledge_graph-Eintrag. ID-Prefix arg_."""
    date_added = date.today().isoformat()
    out = {
        "type": "context",
        "source_collection": source,
        "date_added": date_added,
        "source_file": meta.get("source_file", ""),
        "chunk_index": int(meta.get("chunk_index") or 0),
    }
    if meta.get("category"):
        out["category"] = str(meta.get("category"))
    new_id = f"arg_{doc_id}" if not doc_id.startswith("arg_") else doc_id
    return (new_id, document, _sanitize_metadata(out))


def _migrate_from_chroma(client, dry_run: bool) -> dict[str, int]:
    """Migriert aus live ChromaDB."""
    from src.network.chroma_client import (
        COLLECTION_SIMULATION_EVIDENCE,
        COLLECTION_CORE_DIRECTIVES,
        COLLECTION_SESSION_LOGS,
    )

    counts = {}
    context_col = None
    if not dry_run:
        context_col = client.get_or_create_collection(
            name=COLLECTION_CONTEXT,
            metadata={"description": "MTHO context field (GQA F8)", "hnsw:space": "cosine"},
        )

    transforms = [
        (COLLECTION_SIMULATION_EVIDENCE, _transform_evidence, "simulation_evidence"),
        (COLLECTION_CORE_DIRECTIVES, _transform_directive, "core_directives"),
        (COLLECTION_SESSION_LOGS, _transform_session, "session_logs"),
    ]

    for coll_name, transform_fn, source in transforms:
        try:
            col = client.get_collection(name=coll_name)
        except Exception:
            counts[source] = 0
            continue

        data = col.get(include=["documents", "embeddings", "metadatas"])
        ids = data.get("ids") or []
        if not ids:
            counts[source] = 0
            continue

        documents = data.get("documents") or [""] * len(ids)
        metadatas = data.get("metadatas") or [{}] * len(ids)
        embeddings = data.get("embeddings")

        new_ids, new_docs, new_metas = [], [], []
        for i, (oid, doc, meta) in enumerate(zip(ids, documents, metadatas)):
            nid, ndoc, nmeta = transform_fn(oid, doc or "", meta or {}, source)
            new_ids.append(nid)
            new_docs.append(ndoc)
            new_metas.append(nmeta)

        counts[source] = len(new_ids)
        if dry_run or not context_col:
            continue

        for i in range(0, len(new_ids), BATCH_SIZE):
            batch_ids = new_ids[i : i + BATCH_SIZE]
            batch_docs = new_docs[i : i + BATCH_SIZE]
            batch_meta = new_metas[i : i + BATCH_SIZE]
            if embeddings is not None and len(embeddings) > i:
                batch_emb = embeddings[i : i + BATCH_SIZE]
                batch_emb = [
                    e.tolist() if hasattr(e, "tolist") else list(e) for e in batch_emb
                ]
            else:
                batch_emb = None
            context_col.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=batch_emb,
            )

    # Optional: knowledge_graph
    try:
        from src.network.chroma_client import COLLECTION_KNOWLEDGE_GRAPH

        col = client.get_collection(name=COLLECTION_KNOWLEDGE_GRAPH)
        data = col.get(include=["documents", "embeddings", "metadatas"])
        ids = data.get("ids") or []
        if ids:
            documents = data.get("documents") or [""] * len(ids)
            metadatas = data.get("metadatas") or [{}] * len(ids)
            embeddings = data.get("embeddings")
            new_ids, new_docs, new_metas = [], [], []
            for oid, doc, meta in zip(ids, documents, metadatas):
                nid, ndoc, nmeta = _transform_context(
                    oid, doc or "", meta or {}, "knowledge_graph"
                )
                new_ids.append(nid)
                new_docs.append(ndoc)
                new_metas.append(nmeta)
            counts["knowledge_graph"] = len(new_ids)
            if not dry_run and context_col:
                for i in range(0, len(new_ids), BATCH_SIZE):
                    batch_ids = new_ids[i : i + BATCH_SIZE]
                    batch_docs = new_docs[i : i + BATCH_SIZE]
                    batch_meta = new_metas[i : i + BATCH_SIZE]
                    if embeddings is not None and len(embeddings) > i:
                        batch_emb = [
                            e.tolist() if hasattr(e, "tolist") else list(e)
                            for e in embeddings[i : i + BATCH_SIZE]
                        ]
                    else:
                        batch_emb = None
                    context_col.upsert(
                        ids=batch_ids,
                        documents=batch_docs,
                        metadatas=batch_meta,
                        embeddings=batch_emb,
                    )
        else:
            counts["knowledge_graph"] = 0
    except Exception:
        counts["knowledge_graph"] = 0

    return counts


def _migrate_from_json(json_path: str, client, dry_run: bool) -> dict[str, int]:
    """Migriert aus vps_chroma_full_export.json (ohne Embeddings; ChromaDB erzeugt Default)."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    counts = {}
    context_col = None
    if not dry_run:
        context_col = client.get_or_create_collection(
            name=COLLECTION_CONTEXT,
            metadata={"description": "MTHO context field (GQA F8)", "hnsw:space": "cosine"},
        )

    for coll_key, transform_fn, source in [
        ("simulation_evidence", _transform_evidence, "simulation_evidence"),
        ("core_directives", _transform_directive, "core_directives"),
    ]:
        coll_data = data.get(coll_key)
        if not coll_data or not isinstance(coll_data, dict):
            counts[source] = 0
            continue

        ids = coll_data.get("ids") or []
        documents = coll_data.get("documents") or [""] * len(ids)
        metadatas = coll_data.get("metadatas") or [{}] * len(ids)

        new_ids, new_docs, new_metas = [], [], []
        for oid, doc, meta in zip(ids, documents, metadatas):
            nid, ndoc, nmeta = transform_fn(oid, doc or "", meta or {}, source)
            new_ids.append(nid)
            new_docs.append(ndoc)
            new_metas.append(nmeta)

        counts[source] = len(new_ids)
        if dry_run or not context_col:
            continue

        for i in range(0, len(new_ids), BATCH_SIZE):
            context_col.upsert(
                ids=new_ids[i : i + BATCH_SIZE],
                documents=new_docs[i : i + BATCH_SIZE],
                metadatas=new_metas[i : i + BATCH_SIZE],
            )

    return counts


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Migration zu context_field (GQA F8)")
    ap.add_argument(
        "--source",
        choices=["chroma", "json"],
        default="chroma",
        help="Quelle: chroma (live DB) oder json (Export-Datei)",
    )
    ap.add_argument(
        "--json-path",
        default=str(Path(__file__).resolve().parents[2] / "docs" / "05_AUDIT_PLANNING" / "vps_chroma_full_export.json"),
        help="Pfad zur Export-JSON (nur bei --source json)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Nur zaehlen, nicht schreiben")
    args = ap.parse_args()

    if args.source == "json" and not os.path.exists(args.json_path):
        print(f"JSON nicht gefunden: {args.json_path}")
        sys.exit(1)

    try:
        from src.network.chroma_client import get_chroma_client

        client = get_chroma_client()
    except Exception as e:
        print(f"ChromaDB-Client fehlgeschlagen: {e}")
        sys.exit(1)

    print(f"Migration context_field | Quelle: {args.source} | Dry-Run: {args.dry_run}")
    print("-" * 50)

    if args.source == "json":
        counts = _migrate_from_json(args.json_path, client, args.dry_run)
    else:
        counts = _migrate_from_chroma(client, args.dry_run)

    for k, v in counts.items():
        print(f"  {k}: {v} Eintraege")
    print("-" * 50)
    print(f"Gesamt: {sum(counts.values())} Eintraege")


if __name__ == "__main__":
    main()
