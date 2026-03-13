# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Temporale Konsistenz-Validierung (V12+)

Prueft ob neue Indizien konsistent mit dem bestehenden Wissenskorpus sind.
Erkennt semantischen Drift innerhalb einer Evidenz-Timeline.

Distanz-Schwellwerte:
  < 0.3  = konsistent (nahe Nachbarn)
  0.3-0.8 = akzeptabel (eigenstaendiges Indiz)
  > 0.8  = Drift-Warnung (moeglicher Widerspruch oder Themen-Bruch)
"""
from __future__ import annotations

CONSISTENCY_THRESHOLD = 0.3
DRIFT_THRESHOLD = 0.8


def validate_temporal_consistency(
    new_doc: str,
    collection_name: str = "simulation_evidence",
) -> dict:
    """Prueft ob ein neues Dokument konsistent mit dem bestehenden Korpus ist.

    Nutzt ChromaDB-Semantik-Suche um den naechsten Nachbarn zu finden.

    Returns:
        {"consistent": bool, "nearest_match": str, "distance": float,
         "drift_warning": bool}
    """
    try:
        try:
            from src.network.chroma_client import get_collection
        except ImportError:
            from network.chroma_client import get_collection
        col = get_collection(collection_name, create_if_missing=True)

        existing_count = col.count()
        if existing_count == 0:
            return {
                "consistent": True,
                "nearest_match": "",
                "distance": 0.0,
                "drift_warning": False,
            }

        results = col.query(
            query_texts=[new_doc],
            n_results=1,
        )

        if not results["ids"] or not results["ids"][0]:
            return {
                "consistent": True,
                "nearest_match": "",
                "distance": 0.0,
                "drift_warning": False,
            }

        nearest_id = results["ids"][0][0]
        nearest_doc = results["documents"][0][0] if results.get("documents") else ""
        distance = results["distances"][0][0] if results.get("distances") else 1.0

        return {
            "consistent": distance < CONSISTENCY_THRESHOLD,
            "nearest_match": nearest_id,
            "nearest_preview": nearest_doc[:200] if nearest_doc else "",
            "distance": round(distance, 4),
            "drift_warning": distance > DRIFT_THRESHOLD,
        }

    except Exception as e:
        return {
            "consistent": True,
            "nearest_match": "",
            "distance": -1.0,
            "drift_warning": False,
            "error": str(e),
        }


def detect_drift(evidence_timeline: list[dict]) -> list[dict]:
    """Erkennt semantischen Drift in einer chronologisch sortierten Evidenz-Liste.

    Nimmt aufeinanderfolgende Indizien und berechnet die semantische Distanz.
    Spruenge > DRIFT_THRESHOLD innerhalb derselben Kategorie werden als Drift markiert.

    evidence_timeline: [{"id": str, "document": str, "category": str, ...}, ...]
    (muss chronologisch sortiert sein)

    Returns: Liste von Drift-Events mit Position, Distanz und betroffenen Indizien.
    """
    if len(evidence_timeline) < 2:
        return []

    drift_events: list[dict] = []

    try:
        try:
            from src.network.chroma_client import get_collection
        except ImportError:
            from network.chroma_client import get_collection
        col = get_collection("simulation_evidence", create_if_missing=True)
    except Exception:
        col = None

    for idx in range(len(evidence_timeline) - 1):
        current = evidence_timeline[idx]
        next_ev = evidence_timeline[idx + 1]

        doc_a = current.get("document", "")
        doc_b = next_ev.get("document", "")
        cat_a = current.get("category", "")
        cat_b = next_ev.get("category", "")

        if not doc_a or not doc_b:
            continue

        distance = _compute_semantic_distance(doc_a, doc_b, col)

        same_category = cat_a and cat_b and cat_a == cat_b
        is_drift = distance > DRIFT_THRESHOLD and same_category

        if is_drift:
            drift_events.append({
                "position": idx,
                "from_id": current.get("id", f"idx_{idx}"),
                "to_id": next_ev.get("id", f"idx_{idx + 1}"),
                "category": cat_a,
                "distance": round(distance, 4),
                "severity": "high" if distance > 1.2 else "medium",
                "from_preview": doc_a[:100],
                "to_preview": doc_b[:100],
            })

    return drift_events


def _compute_semantic_distance(doc_a: str, doc_b: str, collection=None) -> float:
    """Berechnet semantische Distanz zwischen zwei Dokumenten.

    Nutzt ChromaDB-Embedding wenn Collection vorhanden, sonst Jaccard-Fallback.
    """
    if collection is not None:
        try:
            temp_id = "__temp_drift_check__"
            try:
                collection.delete(ids=[temp_id])
            except Exception:
                pass

            collection.add(ids=[temp_id], documents=[doc_a])

            results = collection.query(query_texts=[doc_b], n_results=5)

            try:
                collection.delete(ids=[temp_id])
            except Exception:
                pass

            if results["distances"] and results["distances"][0]:
                for i, rid in enumerate(results["ids"][0]):
                    if rid == temp_id:
                        return results["distances"][0][i]

        except Exception:
            pass

    return _jaccard_distance(doc_a, doc_b)


def _jaccard_distance(text_a: str, text_b: str) -> float:
    """Jaccard-Distanz als Fallback fuer semantische Distanz."""
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if not words_a and not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    if not union:
        return 0.0

    jaccard_sim = len(intersection) / len(union)
    return round(1.0 - jaccard_sim, 4)


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    print("=" * 60)
    print("[CORE] Temporale Konsistenz-Validierung – Selbsttest")
    print("=" * 60)

    print("\n--- Jaccard-Distanz (Fallback) ---")
    d1 = _jaccard_distance(
        "Goedels Theorem zeigt formale Grenzen der Berechenbarkeit",
        "Turings Halting Problem zeigt formale Grenzen der Berechenbarkeit",
    )
    d2 = _jaccard_distance(
        "Goedels Theorem zeigt formale Grenzen",
        "Katzen schlafen gerne in der Sonne",
    )
    print(f"  Aehnliche Texte: {d1}")
    print(f"  Verschiedene Texte: {d2}")

    print("\n--- detect_drift (offline) ---")
    timeline = [
        {"id": "ev1", "document": "Goedels Theorem formale Grenzen Logik", "category": "logik"},
        {"id": "ev2", "document": "Turings Halting Problem Berechenbarkeit formale Grenzen", "category": "logik"},
        {"id": "ev3", "document": "Katzen Hunde Tiere Natur Biologie", "category": "logik"},
    ]
    drifts = detect_drift(timeline)
    print(f"  Timeline mit {len(timeline)} Eintraegen")
    print(f"  Drift-Events: {len(drifts)}")
    for d in drifts:
        print(f"    Position {d['position']}: {d['from_id']} -> {d['to_id']} "
              f"(Distanz: {d['distance']}, Schwere: {d['severity']})")

    print("\n--- validate_temporal_consistency ---")
    result = validate_temporal_consistency("Goedels Unvollstaendigkeitssatz")
    print(f"  Ergebnis: {result}")

    print("\n" + "=" * 60)
    print("[CORE] Temporale Validierung operativ.")
    print("=" * 60)
