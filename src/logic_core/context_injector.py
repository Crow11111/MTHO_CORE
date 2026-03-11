# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Context Injector – Kontext & Validierung (Ring-0).

context_injector: Verbindung zu ChromaDB/context_field.
Context Injection: Kontext für Agents (LangChain, Cloud Agents).
Drift Veto: Semantic Drift Block – prüft Output vs. erwarteten Kontext, kann z_widerstand erhöhen.

Integration: gravitator.route_to_context → context_injector → Context Injection
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.config.mtho_state_vector import INV_PHI, get_current_state
# Semantic Drift Threshold: Abweichung > (1 - INV_PHI) → Veto
DRIFT_THRESHOLD = 1.0 - INV_PHI  # ~0.382 (Komplement zu Phi)


@dataclass
class ContextBundle:
    """Kontext-Bündel für Agent-Injection."""

    query: str
    documents: list[str]
    metadatas: list[dict]
    types: list[str]
    scores: list[float]


@dataclass
class VetoResult:
    """Ergebnis des Drift Veto (Semantic Drift Block)."""

    vetoed: bool
    drift_score: float
    z_delta: float
    reason: str


def _get_embedding_function():
    """Lazy ChromaDB DefaultEmbeddingFunction."""
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    return DefaultEmbeddingFunction()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Kosinus-Similarität [0..1] (ChromaDB nutzt cosine distance → 1 - distance)."""
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def fetch_context(
    query_text: str,
    n_results: int = 5,
    type_filter: str | list[str] | None = None,
    use_gravitator: bool = True,
) -> ContextBundle:
    """
    context_injector: Holt Kontext aus context_field für Context Injection.

    Args:
        query_text: Suchanfrage
        n_results: Max. Dokumente
        type_filter: Optional type(s) aus context_field
        use_gravitator: True → route_to_context für semantisches Routing

    Returns:
        ContextBundle mit documents, metadatas, types, scores
    """
    try:
        if use_gravitator:
            from src.network.chroma_client import query_context_via_gravitator

            result = query_context_via_gravitator(
                query_text, n_results=n_results, top_k_types=3
            )
        else:
            from src.network.chroma_client import query_context_field

            result = query_context_field(
                query_text, n_results=n_results, type_filter=type_filter
            )

        ids = result.get("ids", [[]])
        docs = result.get("documents", [[]])
        metas = result.get("metadatas", [[]])
        dists = result.get("distances", [[]])

        if ids and isinstance(ids[0], list):
            ids = ids[0] if ids else []
            docs = docs[0] if docs else []
            metas = metas[0] if metas else []
            dists = dists[0] if dists else []

        types = [m.get("type", "context") if isinstance(m, dict) else "context" for m in metas]
        # ChromaDB cosine distance: kleiner = ähnlicher → Score = max(0, 1 - dist)
        scores = [max(0.0, 1.0 - (d if d is not None else 1.0)) for d in dists] if dists else [0.0] * len(docs)

        return ContextBundle(
            query=query_text,
            documents=list(docs) if docs else [],
            metadatas=list(metas) if metas else [],
            types=types,
            scores=scores,
        )
    except Exception as e:
        return ContextBundle(
            query=query_text,
            documents=[],
            metadatas=[],
            types=[],
            scores=[],
        )


def inject_context_for_agent(
    query_text: str,
    n_results: int = 5,
    format: str = "markdown",
) -> str:
    """
    Context Injection: Formatiert context-field-Daten für Agent-Prompts.

    Args:
        query_text: Suchanfrage
        n_results: Max. Dokumente
        format: "markdown" | "plain"

    Returns:
        Formatierter Kontext-String für System/User-Prompt
    """
    bundle = fetch_context(query_text, n_results=n_results)
    if not bundle.documents:
        return ""

    lines = []
    for i, (doc, meta, score) in enumerate(
        zip(bundle.documents, bundle.metadatas, bundle.scores), 1
    ):
        t = meta.get("type", "?") if isinstance(meta, dict) else "?"
        if format == "markdown":
            lines.append(f"### [{i}] ({t}, score={score:.2f})\n{doc}")
        else:
            lines.append(f"[{t}] {doc}")
    return "\n\n".join(lines)


def check_semantic_drift(
    expected_context: str,
    actual_output: str,
    threshold: float = DRIFT_THRESHOLD,
) -> VetoResult:
    """
    Drift Veto: Prüft ob actual_output vom expected_context abweicht (Semantic Drift).

    Core Stability Anchor: Bei Drift > Threshold → Veto, z_widerstand erhöhen.

    Args:
        expected_context: Erwarteter Kontext (z.B. injizierter context-field-Kontext)
        actual_output: Tatsächlicher Agent-Output
        threshold: Drift-Schwelle (Default: 1 - INV_PHI)

    Returns:
        VetoResult mit vetoed, drift_score, z_delta, reason
    """
    if not expected_context or not actual_output:
        return VetoResult(
            vetoed=False,
            drift_score=0.0,
            z_delta=0.0,
            reason="insufficient_input",
        )

    try:
        ef = _get_embedding_function()
        exp_emb = ef([expected_context.strip()])[0]
        out_emb = ef([actual_output.strip()])[0]
        similarity = _cosine_similarity(list(exp_emb), list(out_emb))
        drift_score = 1.0 - similarity  # Drift = 1 - Similarity
    except Exception:
        return VetoResult(
            vetoed=False,
            drift_score=0.0,
            z_delta=0.0,
            reason="embedding_error",
        )

    vetoed = drift_score > threshold
    z_delta = (drift_score - threshold) * 2.0 if vetoed else 0.0  # Erhöhung proportional
    z_delta = min(0.5, max(0.0, z_delta))

    return VetoResult(
        vetoed=vetoed,
        drift_score=drift_score,
        z_delta=z_delta,
        reason="semantic_drift" if vetoed else "ok",
    )


def apply_veto(veto_result: VetoResult) -> None:
    """
    Wendet Drift Veto an: Erhöht z_widerstand via ring0_state.

    Ruft set_drift_veto mit aktuellem z + z_delta.
    """
    if not veto_result.vetoed or veto_result.z_delta <= 0:
        return
    try:
        from src.config.ring0_state import get_drift_veto_override, set_drift_veto

        current = get_current_state()
        base_z = get_drift_veto_override() if get_drift_veto_override() is not None else current.z_widerstand
        new_z = min(1.0, base_z + veto_result.z_delta)
        set_drift_veto(new_z)
    except Exception:
        pass
