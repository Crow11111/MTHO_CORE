# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Gravitator – Embedding-basiertes Collection-Routing (GQA Refactor F5).
4D-Prisma auf der Diagonalen Strebe.

Routet query_text semantisch zu den relevantesten ChromaDB-Collections
via Kosinus-Similarität gegen Collection-Repräsentanten.

[UPDATE 2026-03-06] ASYNC + TAKT 0 GATE
Integriert Takt 0 Gate und async I/O.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import math
from src.logic_core.takt_gate import check_takt_zero

@dataclass
class CollectionTarget:
    """Ziel-Collection mit Score für GQA-Routing."""

    name: str
    score: float
    type: str  # evidence | directive | session | context | pattern


# Collection-Repräsentanten: Signatur pro Collection (context-field-kompatibel)
_COLLECTION_SIGNATURES: dict[str, tuple[str, str]] = {
    "simulation_evidence": (
        "evidence",
        "Simulationstheorie-Indizien, Evidenz, physikalische und informationstheoretische Argumente, "
        "wissenschaftliche Indizien für oder gegen Simulation, CORE-Klassifikation.",
    ),
    "core_directives": (
        "directive",
        "Ring-0/1 Direktiven, System-Prompts, Governance, Compliance, Paranoia, Bias-Check, "
        "Regeln und Vorgaben für CORE-Verhalten.",
    ),
    "session_logs": (
        "session",
        "Gesprächs-Sessions, Session-Logs, Dialoge, Turn-Turns, Gesprächsverläufe, "
        "Chat-History, Konversationen mit Nutzern.",
    ),
    "knowledge_graph": (
        "context",
        "Knowledge Graph, Kontext, Wissensgraphen, Chunk-Daten, "
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


def _build_representatives_sync() -> list[tuple[str, str, str, list[float]]]:
    """Baut Repräsentanten: (name, type, text, embedding). Sync implementation."""
    from src.config.core_state import state_to_embedding_text

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


async def _get_representatives() -> list[tuple[str, str, str, list[float]]]:
    """Liefert gecachte Repräsentanten (Async Wrapper)."""
    global _REPRESENTATIVES_CACHE
    if _REPRESENTATIVES_CACHE is None:
        _REPRESENTATIVES_CACHE = await asyncio.to_thread(_build_representatives_sync)
    return _REPRESENTATIVES_CACHE


async def route(
    query_text: str,
    top_k: int = 3,
    threshold: float = 0.22,
) -> list[CollectionTarget]:
    """Routet query_text zu den relevantesten Collections (Async).

    Ablauf:
        1. Takt 0 Gate Check (Hard Async Barrier)
        2. query_text → Embedding (in Thread)
        3. Kosinus-Similarität vs. Collection-Repräsentanten
        4. Top-K mit Score > Threshold
        5. Fallback wenn kein Match

    Returns:
        Liste von CollectionTarget, absteigend nach Score.
        Bei Takt 0 Veto: Leere Liste (oder Exception, aber leere Liste ist sicherer Flow).
    """
    # 1. Takt 0 Gate
    gate_open = await check_takt_zero()
    if not gate_open:
        # Request bounces off the membrane
        print(f"[GRAVITATOR] Takt 0 Veto for: '{query_text[:50]}...'")
        return []

    if not query_text or not query_text.strip():
        return list(_FALLBACK_TARGETS)

    # 2. Embedding Calculation (CPU Bound -> Thread)
    try:
        def _calc_query_embedding():
            ef = _get_embedding_function()
            return ef([query_text.strip()])[0]

        query_emb = await asyncio.to_thread(_calc_query_embedding)
    except Exception:
        return list(_FALLBACK_TARGETS)

    # 3. Similarity
    reps = await _get_representatives()
    scored: list[tuple[str, str, float]] = []

    # Calculation is fast enough for main thread usually, but strict simultaneity
    # prefers yielding. We'll do it here as it's pure math on small lists.
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


async def route_to_context(
    query_text: str,
    top_k: int = 3,
    threshold: float = 0.22,
) -> list[CollectionTarget]:
    """Routet zu context_field: Gibt CollectionTarget mit name='context_field' und type zurueck (Async)."""
    targets = await route(query_text, top_k=top_k, threshold=threshold)
    return [
        CollectionTarget(name="context_field", score=t.score, type=t.type)
        for t in targets
    ]
