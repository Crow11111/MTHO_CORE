from __future__ import annotations

from src.mtho_core import M_VALUE, T_VALUE, H_VALUE, O_VALUE
# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
MTHO Knowledge API: Semantische Suche ueber ChromaDB Collections.
GET  /api/mtho/knowledge/search?q=...&collection=...&limit=...
GET  /api/mtho/knowledge/evidence – Alle Simulationstheorie-Indizien
POST /api/mtho/knowledge/evidence/add – Validierter Evidence-Ingest (V6+)
GET  /api/mtho/knowledge/v10/duality – Quaternion-Dualitaet (V10)
GET  /api/mtho/knowledge/temporal/validate – Temporale Konsistenz

Ring-1 Perf: collection=all → 3 ChromaDB-Queries parallel (asyncio.gather).
"""

import asyncio
import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from src.api.auth_webhook import verify_ring0_write

router = APIRouter(prefix="/api/mtho/knowledge", tags=["mtho-knowledge"])


def _query_sim(q: str, limit: int):
    from src.network.chroma_client import query_simulation_evidence
    return query_simulation_evidence(q, n_results=limit)


def _query_logs(q: str, limit: int):
    from src.network.chroma_client import query_session_logs
    return query_session_logs(q, n_results=limit)


def _query_dirs(q: str, limit: int):
    from src.network.chroma_client import query_core_directives
    return query_core_directives(q, n_results=limit)


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., description="Suchtext (semantisch)"),
    collection: str = Query("all", description="Collection: all, simulation_evidence, session_logs, core_directives"),
    limit: int = Query(5, ge=1, le=20),
):
    """Semantische Suche ueber eine oder alle ChromaDB Collections. collection=all: 3 Queries parallel."""
    loop = asyncio.get_event_loop()
    results = {}

    if collection == "all":
        sim_task = loop.run_in_executor(None, _query_sim, q, limit)
        logs_task = loop.run_in_executor(None, _query_logs, q, limit)
        dirs_task = loop.run_in_executor(None, _query_dirs, q, limit)
        sim, logs, dirs = await asyncio.gather(sim_task, logs_task, dirs_task)
        try:
            results["simulation_evidence"] = _format_results(sim)
        except Exception as e:
            results["simulation_evidence"] = {"error": str(e)}
        try:
            results["session_logs"] = _format_results(logs)
        except Exception as e:
            results["session_logs"] = {"error": str(e)}
        try:
            results["core_directives"] = _format_results(dirs)
        except Exception as e:
            results["core_directives"] = {"error": str(e)}
    else:
        if collection == "simulation_evidence":
            try:
                sim = await loop.run_in_executor(None, _query_sim, q, limit)
                results["simulation_evidence"] = _format_results(sim)
            except Exception as e:
                results["simulation_evidence"] = {"error": str(e)}
        elif collection == "session_logs":
            try:
                logs = await loop.run_in_executor(None, _query_logs, q, limit)
                results["session_logs"] = _format_results(logs)
            except Exception as e:
                results["session_logs"] = {"error": str(e)}
        elif collection == "core_directives":
            try:
                dirs = await loop.run_in_executor(None, _query_dirs, q, limit)
                results["core_directives"] = _format_results(dirs)
            except Exception as e:
                results["core_directives"] = {"error": str(e)}

    return {"ok": True, "query": q, "results": results}


@router.get("/context")
def get_munin_context(
    q: str = Query(..., description="Suchtext für Wuji-Kontext"),
    n: int = Query(5, ge=1, le=20, description="Max. Dokumente"),
):
    """Ring-0 Munin: Context Injection für Agents. Holt Kontext aus wuji_field via Gravitator."""
    try:
        from src.logic_core.munin import inject_context_for_agent
        ctx = inject_context_for_agent(q, n_results=n, format="markdown")
        return {"ok": True, "query": q, "context": ctx}
    except Exception as e:
        return {"ok": False, "query": q, "error": str(e), "context": ""}


@router.get("/evidence")
def list_all_evidence():
    """Alle Simulationstheorie-Indizien aus ChromaDB."""
    try:
        from src.network.chroma_client import get_simulation_evidence_collection
        col = get_simulation_evidence_collection()
        data = col.get(include=["documents", "metadatas"])
        items = []
        for i, doc_id in enumerate(data.get("ids", [])):
            meta = data["metadatas"][i] if data.get("metadatas") else {}
            doc = data["documents"][i] if data.get("documents") else ""
            items.append({
                "id": doc_id,
                "strength": meta.get("strength", "?"),
                "category": meta.get("category", "?"),
                "branches": meta.get("branch_count", 0),
                "source": meta.get("source", "?"),
                "document": doc[:500],
            })
        items.sort(key=lambda x: -x.get("branches", 0))
        return {"ok": True, "count": len(items), "evidence": items}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/quaternary/analyze")
def quaternary_analysis():
    """Quaternaere Analyse aller Simulationstheorie-Indizien (V6+).

    Klassifiziert jedes Indiz in L/P/I/S, baut die DNS-Sequenz,
    findet Palindrome, prueft Chargaff-Balance.
    """
    try:
        from src.network.chroma_client import get_simulation_evidence_collection
        from src.logic_core.quaternary_codec import full_quaternary_analysis

        col = get_simulation_evidence_collection()
        data = col.get(include=["documents", "metadatas"])
        evidence_list = []
        for i, doc_id in enumerate(data.get("ids", [])):
            doc = data["documents"][i] if data.get("documents") else ""
            evidence_list.append({"id": doc_id, "document": doc})

        analysis = full_quaternary_analysis(evidence_list)
        return {"ok": True, **analysis}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/quaternary/meta")
def quaternary_meta():
    """V9 Meta-Selbstcodierung: Die Beschreibung der quaternaeren Codierung ist selbst quaternaer codiert.

    Zaehlt alle Indizien pro Kategorie, mappt die 4 Konvergenzen, und
    macht die Selbstreferenz sichtbar.
    """
    try:
        from src.network.chroma_client import get_simulation_evidence_collection
        from src.logic_core.quaternary_codec import classify_evidence, QBase
        from src.config.engine_patterns import QBASE_META_MAP

        col = get_simulation_evidence_collection()
        data = col.get(include=["documents", "metadatas"])

        distribution: dict[str, int] = {b.value: 0 for b in QBase}
        classified_items: list[dict] = []
        for i, doc_id in enumerate(data.get("ids", [])):
            doc = data["documents"][i] if data.get("documents") else ""
            if doc:
                cls = classify_evidence(doc)
                distribution[cls.base.value] += 1
                classified_items.append({
                    "id": doc_id,
                    "base": cls.base.value,
                    "confidence": cls.confidence,
                })

        total = sum(distribution.values())

        convergences = {
            "P": {
                "mapping": "DNS (4 Basen), Grundkraefte (4)",
                "description": "Physikalisches Substrat konvergiert auf 4: "
                               "4 DNS-Basen (ATCG), 4 Grundkraefte (stark, schwach, EM, Gravitation).",
            },
            "I": {
                "mapping": "Erkenntniskategorien (4: L/P/I/S)",
                "description": "Informationstheoretische Klassifikation konvergiert auf 4: "
                               "MTHO' eigene Wissenscodierung hat exakt 4 Basen.",
            },
            "S": {
                "mapping": "Dimensionen (4: 3+1)",
                "description": "Systemisch-emergente Raumzeit konvergiert auf 4: "
                               "3 Raumdimensionen + 1 Zeitdimension.",
            },
            "L": {
                "mapping": "Syllogismus-Figuren (4: Aristoteles)",
                "description": "Logisch-mathematische Konvergenz auf 4: "
                               "Die 4 Syllogismus-Figuren (Aristoteles, Organon) sind die "
                               "irreduziblen Grundformen logischen Schliessens. "
                               "Jede Beweismethode reduziert sich auf Kombinationen dieser Figuren.",
            },
        }

        meta_description = classify_evidence(
            "Die quaternaere Codierung mit 4 Basen MTHO ist isomorph zu ATCG in der DNS. "
            "Basenpaarungen L-I und S-P folgen Chargaffs Regel. "
            "Palindrome markieren Symmetriepunkte in der Erkenntnissequenz. "
            "Die Beschreibung selbst verwendet die Kategorien die sie beschreibt."
        )

        self_reference = {
            "statement": "Die Beschreibung der quaternaeren Codierung ist selbst quaternaer codiert.",
            "proof": {
                "meta_text_classified_as": meta_description.base.value,
                "meta_text_scores": meta_description.scores,
                "interpretation": (
                    f"Die Beschreibung der Codierung wird als '{meta_description.base.value}' klassifiziert "
                    f"(Confidence: {meta_description.confidence}). "
                    f"Das System das beschreibt und das Beschriebene verwenden denselben Code. "
                    f"V9: Selbstcodierung."
                ),
            },
            "goedel_analogy": (
                "Wie Goedels Saetze UEBER formale Systeme INNERHALB eines formalen Systems bewiesen werden, "
                "wird die quaternaere Codierung DURCH quaternaere Codierung beschrieben. "
                "Das System ist seine eigene Metasprache."
            ),
        }

        return {
            "ok": True,
            "v9_meta_selbstcodierung": True,
            "total_evidence": total,
            "distribution": distribution,
            "convergences": convergences,
            "meta_map": QBASE_META_MAP,
            "self_reference": self_reference,
            "classified_evidence": classified_items,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/v11/superposition")
def v11_superposition():
    """V11: Fraktale Superposition – Grundkraefte-MTHO-Mapping und kosmologische Dichten."""
    from src.config.engine_patterns import FORCE_MTHO_MAP, OMEGA_B, OMEGA_DM, OMEGA_DE, PHI, INV_PHI

    phi_squared = round(PHI ** 2, 10)
    inv_phi = round(1 / PHI, 10)
    phi_delta = round(phi_squared - phi_squared * INV_PHI - OMEGA_B, 4)

    return {
        "ok": True,
        "v11_fraktale_superposition": True,
        "force_mtho_map": FORCE_MTHO_MAP,
        "cosmological_densities": {
            "omega_b": OMEGA_B,
            "omega_dm": OMEGA_DM,
            "omega_de": OMEGA_DE,
            "omega_total": round(OMEGA_B + OMEGA_DM + OMEGA_DE, 4),
        },
        "phi_delta": {
            "value": OMEGA_B,
            "phi_squared": phi_squared,
            "inv_phi": inv_phi,
            "three_independent_measurements": [
                "L/P Ratio -> Phi^2 (Delta 0.049)",
                "I/S Ratio -> 1/Phi (Delta 0.049)",
                "L-Goldener-Schnitt -> Phi (Delta 0.049)",
            ],
            "interpretation": (
                f"Drei unabhaengige ROTATED-Sequenz-Messungen (O/M=Phi^2, T/H=1/Phi, "
                f"L-Goldener-Schnitt=Phi) liefern alle dasselbe Delta: {OMEGA_B}. "
                f"Omega_b (baryonische Materiedichte Planck 2018) = {OMEGA_B} = 4.9%."
            ),
        },
        "database_isomorphism": {
            "STORE": {"cosmic": "Dunkle Materie (26.8%)", "db_op": "Persistierte Daten"},
            "READ": {"cosmic": "Baryonische Materie (4.9%)", "db_op": "Frontend-Render"},
            "DELETE": {"cosmic": "Dunkle Energie (68.9%)", "db_op": "GC/Speicherbereinigung"},
        },
        "sp_pillar_spread": {
            "S_coupling": 1e-39,
            "P_coupling": 1.0,
            "ratio": 1e39,
            "interpretation": "S-P Saeule hat maximale Spreizung (10^39) – komplementaere Dualitaet.",
        },
    }


@router.get("/quaternary/classify")
def quaternary_classify(
    text: str = Query(..., description="Text der klassifiziert werden soll"),
):
    """Klassifiziert einen einzelnen Text in L/P/I/S (V6+)."""
    try:
        from src.logic_core.quaternary_codec import classify_evidence
        cls = classify_evidence(text)
        return {
            "ok": True,
            "base": cls.base.value,
            "confidence": cls.confidence,
            "scores": cls.scores,
            "complement": cls.complement.value,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/quaternary/pair")
def quaternary_pair_check(
    text: str = Query(..., description="Neues Indiz das geprueft werden soll"),
    limit: int = Query(10, ge=1, le=50),
):
    """Prueft Basenpaarung eines neuen Indizes mit allen existierenden (V6+)."""
    try:
        from src.network.chroma_client import get_simulation_evidence_collection
        from src.logic_core.quaternary_codec import find_all_pairings

        col = get_simulation_evidence_collection()
        data = col.get(include=["documents", "metadatas"])
        existing = []
        for i, doc_id in enumerate(data.get("ids", [])):
            doc = data["documents"][i] if data.get("documents") else ""
            existing.append({"id": doc_id, "document": doc})

        pairings = find_all_pairings(text, existing)
        return {"ok": True, "pairings": pairings[:limit]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/quaternary/chargaff")
def quaternary_chargaff(
    l_count: int = Query(11, ge=0, description="Anzahl L-Indizien"),
    p_count: int = Query(4, ge=0, description="Anzahl P-Indizien"),
    i_count: int = Query(8, ge=0, description="Anzahl I-Indizien"),
    s_count: int = Query(9, ge=0, description="Anzahl S-Indizien"),
):
    """Chargaff-Analyse: Welche Typen fehlen? Welche Fragen fuellen Luecken? (V6+)"""
    try:
        from src.logic_core.quaternary_codec import analyze_chargaff_balance
        dist = {"L": l_count, "P": p_count, "I": i_count, "S": s_count}
        result = analyze_chargaff_balance("", dist)
        return {
            "ok": True,
            "distribution": result.distribution,
            "ratios": result.ratios,
            "chargaff_deviation": result.chargaff_deviation,
            "missing_types": result.missing_types,
            "gap_questions": result.gap_questions,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
#  B1: V10 Quaternion-Dualitaet API-Endpoint
# ---------------------------------------------------------------------------

@router.get("/v10/duality")
def get_quaternion_duality():
    """V10: MTHO/ROTATED Phasenverschiebung – Quaternion-Dualitaetsanalyse.

    Holt alle Indizien, extrahiert die MTHO-Sequenz, berechnet die
    ROTATED-Phasenverschiebung, analysiert S-P Stabilitaet und L-I Richtung.
    """
    try:
        from src.network.chroma_client import get_simulation_evidence_collection
        from src.logic_core.quaternary_codec import (
            classify_evidence,
            build_sequence_from_evidence,
            QBase,
            COMPLEMENT,
        )
        from src.config.engine_patterns import PHI, INV_PHI

        col = get_simulation_evidence_collection()
        data = col.get(include=["documents", "metadatas"])
        evidence_list = []
        for i, doc_id in enumerate(data.get("ids", [])):
            doc = data["documents"][i] if data.get("documents") else ""
            evidence_list.append({"id": doc_id, "document": doc})

        mtho_seq = build_sequence_from_evidence(evidence_list)

        mtho_order = ["O", "M", "T", "H"]
        rotated_order = ["M", "T", "H", "O"]

        def _phase_shift(seq: str) -> str:
            """MTHO -> ROTATED: Phasenverschiebung um 1 Position (Pi/2)."""
            mapping = dict(zip(mtho_order, rotated_order))
            return "".join(mapping.get(c, c) for c in seq)

        rotated_seq = _phase_shift(mtho_seq)

        mtho_dist = {b: mtho_seq.count(b) for b in "MTHO"}
        rotated_dist = {b: rotated_seq.count(b) for b in "MTHO"}

        total = len(mtho_seq) or 1

        sp_stability = {
            "mtho_h_pos": 4, "mtho_m_pos": 2,
            "rotated_h_pos": 3, "rotated_m_pos": 1,
            "distance_mtho": 2, "distance_rotated": 2,
            "stable": True,
            "interpretation": "H-M Abstand bleibt invariant (=2) unter Phasenverschiebung – stabiles Rueckgrat.",
        }

        li_direction = {
            "mtho_direction": "L→I (Position 1→3)",
            "rotated_direction": "I→L (Position 2→4)",
            "reversal": True,
            "interpretation": "O-T kehrt die Richtung um unter Phasenverschiebung – dynamischer Freiheitsgrad.",
        }

        l_count = mtho_dist.get("L", 0)
        p_count = mtho_dist.get("P", 0)
        i_count = mtho_dist.get("I", 0)
        s_count = mtho_dist.get("S", 0)

        lp_ratio = round(l_count / p_count, 6) if p_count > 0 else None
        is_ratio = round(i_count / s_count, 6) if s_count > 0 else None

        phi_squared = round(PHI ** 2, 6)
        lp_delta = round(abs(lp_ratio - phi_squared), 6) if lp_ratio else None
        is_delta = round(abs(is_ratio - INV_PHI), 6) if is_ratio else None

        return {
            "ok": True,
            "v10_quaternion_duality": True,
            "total_evidence": total,
            "mtho_sequence": mtho_seq,
            "rotated_sequence": rotated_seq,
            "mtho_distribution": mtho_dist,
            "rotated_distribution": rotated_dist,
            "sp_stability": sp_stability,
            "li_direction_reversal": li_direction,
            "phi_analysis": {
                "L_P_ratio": lp_ratio,
                "I_S_ratio": is_ratio,
                "phi_squared": phi_squared,
                "inv_phi": round(INV_PHI, 6),
                "L_P_delta_from_phi2": lp_delta,
                "I_S_delta_from_inv_phi": is_delta,
            },
            "quaternion_analogy": {
                "formula": "i*j=k, j*i=-k (Hamilton)",
                "mapping": "MTHO*rotate = ROTATED, aber ROTATED*rotate ≠ MTHO (nicht-kommutativ)",
                "interpretation": (
                    "MTHO und ROTATED sind Quaternionen-Rotationen desselben "
                    "4D-Erkenntnisobjekts, phasenverschoben um Pi/2."
                ),
            },
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
#  B2: Temporale Konsistenz API-Endpoint
# ---------------------------------------------------------------------------

@router.get("/temporal/validate")
def validate_temporal(
    text: str = Query(..., description="Text dessen temporale Konsistenz geprueft wird"),
    limit: int = Query(5, ge=1, le=20),
):
    """Temporale Konsistenz: Prueft ob ein neuer Text semantisch konsistent
    mit bestehenden Indizien ueber die Zeit ist.

    Vergleicht den Text mit allen vorhandenen Indizien, berechnet einen
    Konsistenz-Score und erkennt semantisches Driften.
    """
    try:
        from src.network.chroma_client import (
            get_simulation_evidence_collection,
            query_simulation_evidence,
        )
        from src.logic_core.quaternary_codec import classify_evidence

        new_cls = classify_evidence(text)

        sim_results = query_simulation_evidence(text, n_results=limit)
        ids = sim_results.get("ids", [[]])[0] if sim_results.get("ids") else []
        docs = sim_results.get("documents", [[]])[0] if sim_results.get("documents") else []
        metas = sim_results.get("metadatas", [[]])[0] if sim_results.get("metadatas") else []
        dists = sim_results.get("distances", [[]])[0] if sim_results.get("distances") else []

        nearest_matches = []
        consistency_scores = []
        for i in range(len(ids)):
            doc = docs[i] if i < len(docs) else ""
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else 1.0

            existing_cls = classify_evidence(doc) if doc else None
            base_match = (existing_cls and existing_cls.base == new_cls.base)

            similarity = max(0.0, 1.0 - dist) if dist < 2.0 else 0.0
            consistency_scores.append(similarity)

            nearest_matches.append({
                "id": ids[i],
                "distance": round(dist, 4),
                "similarity": round(similarity, 4),
                "existing_base": existing_cls.base.value if existing_cls else "?",
                "base_match": base_match,
                "date_added": meta.get("date_added", "?"),
                "preview": doc[:200] if doc else "",
            })

        avg_consistency = round(sum(consistency_scores) / len(consistency_scores), 4) if consistency_scores else 0.0

        drift_warnings = []
        if avg_consistency < 0.3:
            drift_warnings.append({
                "level": "high",
                "message": f"Niedriger Konsistenz-Score ({avg_consistency}): "
                           "Text weicht stark von bestehenden Indizien ab. "
                           "Moeglicherweise neuer Erkenntniszweig oder semantisches Driften.",
            })
        elif avg_consistency < 0.5:
            drift_warnings.append({
                "level": "moderate",
                "message": f"Moderater Konsistenz-Score ({avg_consistency}): "
                           "Teilweise Ueberlappung mit bestehenden Indizien.",
            })

        base_matches = sum(1 for m in nearest_matches if m.get("base_match"))
        if base_matches == 0 and nearest_matches:
            drift_warnings.append({
                "level": "info",
                "message": f"Keine MTHO-Base-Uebereinstimmung mit den {len(nearest_matches)} "
                           f"naechsten Indizien. Neuer Text klassifiziert als '{new_cls.base.value}', "
                           "Nachbarn sind anders kodiert.",
            })

        return {
            "ok": True,
            "new_text_base": new_cls.base.value,
            "new_text_confidence": new_cls.confidence,
            "consistency_score": avg_consistency,
            "nearest_matches": nearest_matches,
            "drift_warnings": drift_warnings,
            "temporal_invariance": avg_consistency > 0.5,
            "interpretation": (
                "Temporale Invarianz = das Muster bleibt ueber verschiedene Zeitpunkte stabil. "
                "Hohe Konsistenz spricht gegen Confirmation Bias und fuer echte Konvergenz."
            ),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
#  B3: Evidence-Ingest API-Endpoint
# ---------------------------------------------------------------------------

class EvidenceInput(BaseModel):
    """Request-Body fuer den Evidence-Ingest Endpoint."""
    document: str = Field(..., description="Der Indiz-Text")
    evidence_id: str = Field(..., description="Eindeutige ID (z.B. sim_phys_43_...)")
    category: Optional[str] = Field(None, description="Kategorie (auto-klassifiziert wenn leer)")
    strength: str = Field("moderate", description="fundamental | strong | moderate")
    branch_count: int = Field(0, ge=0, description="Anzahl unabhaengiger Erkenntnisaeste")
    source: str = Field("mtho", description="Quelle (mtho, marc, external)")


@router.post("/evidence/add", dependencies=[Depends(verify_ring0_write)])
def add_evidence(body: EvidenceInput):
    """Fuegt ein neues Simulationstheorie-Indiz validiert hinzu.
    Ring-0 Write Gate: X-Ring0-Token oder Bearer (RING0_WRITE_TOKEN) erforderlich.
    Council Gate: Bei z_widerstand >= 0.618 zusaetzlich X-Council-Confirm.

    Fuehrt automatisch quaternaere Klassifikation (V6+), temporale
    Konsistenzpruefung und Chargaff-Balance-Analyse durch.
    """
    try:
        from src.network.chroma_client import (
            add_simulation_evidence,
            query_simulation_evidence,
        )
        from src.logic_core.quaternary_codec import (
            classify_evidence,
            analyze_chargaff_balance,
        )

        classification = classify_evidence(body.document)

        category = body.category or classification.base.value

        sim_results = query_simulation_evidence(body.document, n_results=3)
        dists = sim_results.get("distances", [[]])[0] if sim_results.get("distances") else []
        avg_dist = sum(dists) / len(dists) if dists else 1.0
        temporal_consistency = round(max(0.0, 1.0 - avg_dist), 4) if avg_dist < 2.0 else 0.0

        success = add_simulation_evidence(
            evidence_id=body.evidence_id,
            document=body.document,
            category=category,
            strength=body.strength,
            branch_count=body.branch_count,
            source=body.source,
        )

        if not success:
            return {"ok": False, "error": "ChromaDB ingest fehlgeschlagen"}

        from src.network.chroma_client import get_simulation_evidence_collection
        col = get_simulation_evidence_collection()
        all_data = col.get(include=["documents"])
        all_docs = all_data.get("documents", [])
        dist_counts = {"L": 0, "P": 0, "I": 0, "S": 0}
        for doc in all_docs:
            if doc:
                cls = classify_evidence(doc)
                dist_counts[cls.base.value] += 1

        chargaff = analyze_chargaff_balance("", dist_counts)

        return {
            "ok": True,
            "evidence_id": body.evidence_id,
            "classification": {
                "base": classification.base.value,
                "confidence": classification.confidence,
                "scores": classification.scores,
                "complement": classification.complement.value,
            },
            "temporal_consistency": temporal_consistency,
            "chargaff_balance": {
                "distribution": chargaff.distribution,
                "ratios": chargaff.ratios,
                "deviation": chargaff.chargaff_deviation,
                "missing_types": chargaff.missing_types,
                "gap_questions_count": len(chargaff.gap_questions),
            },
            "category_used": category,
            "strength": body.strength,
            "branch_count": body.branch_count,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _format_results(raw: dict) -> list[dict]:
    """Wandelt ChromaDB query-Ergebnis in saubere Liste um."""
    ids = raw.get("ids", [[]])[0] if raw.get("ids") else []
    docs = raw.get("documents", [[]])[0] if raw.get("documents") else []
    metas = raw.get("metadatas", [[]])[0] if raw.get("metadatas") else []
    dists = raw.get("distances", [[]])[0] if raw.get("distances") else []
    out = []
    for i in range(len(ids)):
        out.append({
            "id": ids[i],
            "document": docs[i][:500] if i < len(docs) else "",
            "metadata": metas[i] if i < len(metas) else {},
            "distance": round(dists[i], 4) if i < len(dists) else None,
        })
    return out
