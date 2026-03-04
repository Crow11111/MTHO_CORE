"""
Gravitator – Embedding-basiertes Collection-Routing (GQA Refactor F5).

Routet query_text semantisch zu den relevantesten ChromaDB-Collections
via Kosinus-Similarität gegen Collection-Repräsentanten.

Repräsentanten nutzen state_to_embedding_text() + Collection-Signatur.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
@dataclass
class CollectionTarget:
    """Ziel-Collection mit Score für GQA-Routing."""

    name: str
    score: float
    type: str  # evidence | directive | session | context | pattern


# Collection-Repräsentanten: Signatur pro Collection (Wuji-Feld-kompatibel)
_COLLECTION_SIGNATURES: dict[str, tuple[str, str]] = {
    "simulation_evidence": (
        "evidence",
        "Simulationstheorie-Indizien, Evidenz, physikalische und informationstheoretische Argumente, "
        "wissenschaftliche Indizien für oder gegen Simulation, LPIS-Klassifikation.",
    ),
    "core_directives": (
        "directive",
        "Ring-0/1 Direktiven, System-Prompts, Governance, Compliance, Paranoia, Bias-Check, "
        "Regeln und Vorgaben für ATLAS-Verhalten.",
    ),
    "session_logs": (
        "session",
        "Gesprächs-Sessions, Session-Logs, Dialoge, Turn-Turns, Gesprächsverläufe, "
        "Chat-History, Konversationen mit Nutzern.",
    ),
    "argos_knowledge_graph": (
        "context",
        "Argos Knowledge Graph, Kontext, Wissensgraphen, Chunk-Daten, "
        "dokumentierte Architektur und Konzepte.",
    ),
    "marc_li_patterns": (
        "pattern",
        "Marc-LI Patterns, ND-Patterns, Muster, neurodivergente Verhaltensmuster, "
        "L-I Paarung, strukturelle Muster.",
    ),
}

# Fallback wenn kein Match: breiteste Collections zuerst
_FALLBACK_TARGETS: list[CollectionTarget] = [
    CollectionTarget("simulation_evidence", 0.0, "evidence"),
    CollectionTarget("core_directives", 0.0, "directive"),
]


def _get_embedding_function():
    """Lazy-Import ChromaDB DefaultEmbeddingFunction (384 dim, all-MiniLM-L6-v2)."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    return DefaultEmbeddingFunction()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Kosinus-Similarität zwischen zwei Vektoren. Bereich [-1, 1]."""
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _build_representatives() -> list[tuple[str, str, str, list[float]]]:
    """Baut Repräsentanten: (name, type, text, embedding)."""
    from src.config.atlas_state_vector import state_to_embedding_text

    base_text = state_to_embedding_text()
    ef = _get_embedding_function()

    result = []
    for name, (ctype, sig) in _COLLECTION_SIGNATURES.items():
        full_text = base_text + "\n" + sig
        emb = ef([full_text])[0]
        result.append((name, ctype, full_text, emb))
    return result


# Cache der Repräsentanten-Embeddings (einmalig berechnet)
_REPRESENTATIVES_CACHE: list[tuple[str, str, str, list[float]]] | None = None


def _get_representatives() -> list[tuple[str, str, str, list[float]]]:
    """Liefert gecachte Repräsentanten."""
    global _REPRESENTATIVES_CACHE
    if _REPRESENTATIVES_CACHE is None:
        _REPRESENTATIVES_CACHE = _build_representatives()
    return _REPRESENTATIVES_CACHE


def route(
    query_text: str,
    top_k: int = 3,
    threshold: float = 0.22,
) -> list[CollectionTarget]:
    """Routet query_text zu den relevantesten Collections.

    Ablauf:
        1. query_text → Embedding
        2. Kosinus-Similarität vs. Collection-Repräsentanten
        3. Top-K mit Score > Threshold
        4. Fallback: simulation_evidence + core_directives wenn kein Match

    Args:
        query_text: Suchanfrage
        top_k: Max. Anzahl Collections (Default: 3)
        threshold: Min. Kosinus-Similarität (Default: 0.22)

    Returns:
        Liste von CollectionTarget, absteigend nach Score.
        Bei Fallback: score=0.0 als Indikator.
    """
    if not query_text or not query_text.strip():
        return list(_FALLBACK_TARGETS)

    try:
        ef = _get_embedding_function()
        query_emb = ef([query_text.strip()])[0]
    except Exception:
        return list(_FALLBACK_TARGETS)

    reps = _get_representatives()
    scored: list[tuple[str, str, float]] = []
    for name, ctype, _text, rep_emb in reps:
        score = _cosine_similarity(list(query_emb), list(rep_emb))
        scored.append((name, ctype, score))

    # Sortieren absteigend nach Score
    scored.sort(key=lambda x: -x[2])

    # Filter: Score > Threshold, Top-K
    matches = [s for s in scored if s[2] >= threshold][:top_k]

    if not matches:
        return list(_FALLBACK_TARGETS)

    return [
        CollectionTarget(name=name, score=score, type=ctype)
        for name, ctype, score in matches
    ]
