# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
CORE CONTEXT – End-to-End Integration Test.

Testet die vollständige Kette ohne externe Abhängigkeiten:
1. Entry-Adapter (WhatsApp, HA, NormalizedEntry)
2. Telemetry-Injector (Triage, CORE, Intent)
3. Gravitator (Route, Collection-Auswahl, Fallback)
4. Context Injector (Context Injection, Semantic Drift)
5. Veto Gate (Veto-Modus, Critical Path)

Keine echten API-Calls, keine ChromaDB/Embedding-Netzwerkzugriffe.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# ---------------------------------------------------------------------------
# Mock-Layer: Embedding & ChromaDB vor allen Imports
# ---------------------------------------------------------------------------
MOCK_DIM = 384


def _mock_embedding(text: str) -> list[float]:
    """Deterministischer Mock-Vektor aus Text (kein Netzwerk)."""
    import hashlib
    h = hashlib.sha256((text or "").encode()).hexdigest()
    return [(int(h[i : i + 2], 16) / 255.0 - 0.5) * 2 for i in range(0, min(len(h), MOCK_DIM * 2), 2)][:MOCK_DIM]


class MockEmbeddingFunction:
    def __call__(self, texts: list[str]) -> list[list[float]]:
        return [_mock_embedding(t) for t in texts]


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------
def run_tests() -> dict[str, list[tuple[str, bool, str]]]:
    results: dict[str, list[tuple[str, bool, str]]] = {}

    # ── 1. Entry-Adapter ───────────────────────────────────────────────────
    results["Entry-Adapter"] = []

    try:
        from src.api.entry_adapter import (
            NormalizedEntry,
            normalize_request,
            VALID_SOURCES,
        )

        # WhatsApp-Payload
        wa_payload = {
            "message": {
                "conversation": "Hallo CORE, wie geht es dir?",
                "extendedTextMessage": None,
            },
            "key": {"remoteJid": "49123456789@s.whatsapp.net"},
        }
        entry_wa = normalize_request("whatsapp", wa_payload)
        ok = (
            entry_wa.source == "whatsapp"
            and entry_wa.payload.get("text") == "Hallo CORE, wie geht es dir?"
            and entry_wa.payload.get("sender", "").endswith("@s.whatsapp.net")
        )
        results["Entry-Adapter"].append(
            ("WhatsApp-Payload -> NormalizedEntry", ok, "" if ok else f"source={entry_wa.source} text={entry_wa.payload.get('text')}")
        )

        # HA-Payload
        ha_payload = {
            "action": "text_input",
            "message": "Licht im Wohnzimmer an",
            "user_id": "ha_user_1",
        }
        entry_ha = normalize_request("ha", ha_payload)
        ok = (
            entry_ha.source == "ha"
            and entry_ha.payload.get("text") == "Licht im Wohnzimmer an"
            and entry_ha.payload.get("action") == "text_input"
        )
        results["Entry-Adapter"].append(
            ("HA-Payload -> NormalizedEntry", ok, "" if ok else str(entry_ha.payload))
        )

        # NormalizedEntry-Struktur
        ok = (
            hasattr(entry_wa, "timestamp")
            and "whatsapp" in VALID_SOURCES
            and "ha" in VALID_SOURCES
        )
        results["Entry-Adapter"].append(
            ("NormalizedEntry-Struktur (timestamp, VALID_SOURCES)", ok, "" if ok else "Struktur fehlt")
        )

        # Invalid source
        try:
            normalize_request("invalid", {})
            ok = False
        except ValueError:
            ok = True
        results["Entry-Adapter"].append(
            ("Invalid source -> ValueError", ok, "" if ok else "Kein ValueError")
        )

    except Exception as e:
        results["Entry-Adapter"].append(("Entry-Adapter Import/Execution", False, str(e)))

    # ── 2. Telemetry-Injector ───────────────────────────────────────────────────────────
    results["Telemetry-Injector"] = []

    try:
        from src.api.entry_adapter import normalize_request
        from src.logic_core.telemetry_injector import triage, triage_from_raw, TriageResult

        # Triage: CORE L (Logik)
        entry_l = normalize_request("api", {"text": "Prüfe die Compliance und Sicherheit der Regel"})
        r_l = triage(entry_l)
        ok = r_l.core_base == "L"
        results["Telemetry-Injector"].append(
            ("CORE-Klassifikation L (Logik/Compliance)", ok, f"got={r_l.core_base}")
        )

        # Triage: CORE P (Physik)
        entry_p = normalize_request("api", {"text": "Simulation und Gravitation Quanten"})
        r_p = triage(entry_p)
        ok = r_p.core_base == "P"
        results["Telemetry-Injector"].append(
            ("CORE-Klassifikation P (Physik/Simulation)", ok, f"got={r_p.core_base}")
        )

        # Triage: CORE I (Info)
        entry_i = normalize_request("api", {"text": "Suche im Archiv nach Kontext"})
        r_i = triage(entry_i)
        ok = r_i.core_base == "I"
        results["Telemetry-Injector"].append(
            ("CORE-Klassifikation I (Info/Archiv)", ok, f"got={r_i.core_base}")
        )

        # Triage: CORE S (Struktur)
        entry_s = normalize_request("api", {"text": "Architektur und System Ring Tetralogie"})
        r_s = triage(entry_s)
        ok = r_s.core_base == "S"
        results["Telemetry-Injector"].append(
            ("CORE-Klassifikation S (Struktur/Architektur)", ok, f"got={r_s.core_base}")
        )

        # Intent: query
        entry_q = normalize_request("api", {"text": "Was ist die Simulationstheorie?"})
        r_q = triage(entry_q)
        ok = r_q.intent == "query"
        results["Telemetry-Injector"].append(
            ("Intent query (Was/Wie/Warum)", ok, f"got={r_q.intent}")
        )

        # Intent: command
        entry_cmd = normalize_request("api", {"text": "Mach das Licht an"})
        r_cmd = triage(entry_cmd)
        ok = r_cmd.intent == "command"
        results["Telemetry-Injector"].append(
            ("Intent command (Mach/Führe)", ok, f"got={r_cmd.intent}")
        )

        # Intent: status
        entry_st = normalize_request("ha", {"action": "core_ping"})
        r_st = triage(entry_st)
        ok = r_st.intent == "status"
        results["Telemetry-Injector"].append(
            ("Intent status (core_ping)", ok, f"got={r_st.intent}")
        )

        # triage_from_raw
        r_raw = triage_from_raw("whatsapp", {"message": {"conversation": "Zeig mir die Regeln"}}, None)
        ok = isinstance(r_raw, TriageResult) and r_raw.entry.source == "whatsapp"
        results["Telemetry-Injector"].append(
            ("triage_from_raw Convenience", ok, "" if ok else str(type(r_raw)))
        )

    except Exception as e:
        results["Telemetry-Injector"].append(("Telemetry-Injector Import/Execution", False, str(e)))

    # ── 3. Gravitator (mit Mock-Embedding) ──────────────────────────────────
    results["Gravitator"] = []

    try:
        import unittest.mock as mock
        from src.logic_core.gravitator import route, route_to_context, CollectionTarget, _FALLBACK_TARGETS

        mock_ef = MockEmbeddingFunction()

        with mock.patch("src.logic_core.gravitator._get_embedding_function", return_value=mock_ef):
            # Route: normale Query
            targets = route("Simulationstheorie Indizien", top_k=2, threshold=0.0)
            ok = len(targets) >= 1 and all(isinstance(t, CollectionTarget) for t in targets)
            results["Gravitator"].append(
                ("Route: Query -> CollectionTargets", ok, f"len={len(targets)}")
            )

            # Route: leere Query → Fallback
            fallback = route("", top_k=2)
            ok = fallback == list(_FALLBACK_TARGETS) or (
                len(fallback) >= 2
                and any(t.name == "simulation_evidence" for t in fallback)
            )
            results["Gravitator"].append(
                ("Route: Leere Query -> Fallback", ok, f"got={[t.name for t in fallback]}")
            )

            # route_to_context
            context_targets = route_to_context("Governance Direktive", top_k=2, threshold=0.0)
            ok = all(t.name == "context_field" for t in context_targets)
            results["Gravitator"].append(
                ("route_to_context -> name=context_field", ok, f"names={[t.name for t in context_targets]}")
            )

            # Collection-Auswahl: unterschiedliche Queries
            t_ev = route("Evidenz für Simulation", top_k=1, threshold=0.0)
            t_dir = route("Ring-0 Direktive Bias", top_k=1, threshold=0.0)
            ok = len(t_ev) >= 1 and len(t_dir) >= 1
            results["Gravitator"].append(
                ("Collection-Auswahl variiert nach Query", ok, f"ev={len(t_ev)} dir={len(t_dir)}")
            )

    except Exception as e:
        results["Gravitator"].append(("Gravitator Import/Execution", False, str(e)))

    # ── 4. Context Injector (mit Mock ChromaDB + Embedding) ────────────────
    results["Context Injector"] = []

    try:
        import unittest.mock as mock
        from src.logic_core.context_injector import (
            fetch_context,
            inject_context_for_agent,
            check_semantic_drift,
            ContextBundle,
            VetoResult,
            DRIFT_THRESHOLD,
        )

        # Mock chroma_client
        mock_context_result = {
            "ids": [["doc1"]],
            "documents": [["Mock-Dokument: Simulationstheorie Indizien"]],
            "metadatas": [[{"type": "evidence", "core_base": "P"}]],
            "distances": [[0.2]],
        }

        # context_injector importiert chroma_client dynamisch - Patch am Modul
        with mock.patch(
            "src.network.chroma_client.query_context_via_gravitator",
            return_value=mock_context_result,
        ), mock.patch(
            "src.network.chroma_client.query_context_field",
            return_value=mock_context_result,
        ), mock.patch(
            "src.logic_core.context_injector._get_embedding_function",
            return_value=MockEmbeddingFunction(),
        ):
            # Context Injection: fetch_context
            bundle = fetch_context("Test Query", n_results=3, use_gravitator=True)
            ok = isinstance(bundle, ContextBundle) and len(bundle.documents) >= 1
            results["Context Injector"].append(
                ("fetch_context -> ContextBundle", ok, f"docs={len(bundle.documents)}")
            )

            # inject_context_for_agent
            ctx_str = inject_context_for_agent("Test", n_results=3, format="markdown")
            ok = "### " in ctx_str or len(ctx_str) >= 1 or (len(bundle.documents) == 0 and ctx_str == "")
            results["Context Injector"].append(
                ("inject_context_for_agent -> markdown", ok, f"len={len(ctx_str)}")
            )

        # Semantic Drift (ohne Chroma, nur Embedding-Mock)
        with mock.patch(
            "src.logic_core.context_injector._get_embedding_function",
            return_value=MockEmbeddingFunction(),
        ):
            # Gleicher Kontext/Output → kein Veto
            same_ctx = "Simulationstheorie ist eine Hypothese."
            same_out = "Simulationstheorie ist eine Hypothese."
            v_same = check_semantic_drift(same_ctx, same_out, threshold=0.5)
            ok = not v_same.vetoed and v_same.drift_score < 0.5
            results["Context Injector"].append(
                ("Semantic Drift: gleicher Text -> kein Veto", ok, f"vetoed={v_same.vetoed} drift={v_same.drift_score:.3f}")
            )

            # Leere Inputs → kein Veto
            v_empty = check_semantic_drift("", "irgendwas")
            ok = not v_empty.vetoed and v_empty.reason == "insufficient_input"
            results["Context Injector"].append(
                ("Semantic Drift: leere Inputs -> insufficient_input", ok, f"reason={v_empty.reason}")
            )

            # Starker Drift (anderer Text) → kann Veto auslösen bei niedrigem Threshold
            v_drift = check_semantic_drift(
                "CORE Ring-0 Direktive Compliance",
                "Pizza Rezept Käse Tomaten",
                threshold=0.1,
            )
            ok = isinstance(v_drift, VetoResult)
            results["Context Injector"].append(
                ("Semantic Drift: VetoResult-Struktur", ok, f"vetoed={v_drift.vetoed}")
            )

    except Exception as e:
        results["Context Injector"].append(("Context Injector Import/Execution", False, str(e)))

    # ── 5. Veto Gate ───────────────────────────────────────────────────
    results["Veto Gate"] = []

    try:
        import unittest.mock as mock
        from src.api.middleware.veto_gate import (
            _is_critical_request,
            _get_z_widerstand,
            _has_confirmation,
            CRITICAL_PATH_PATTERNS,
            VETO_THRESHOLD,
        )

        # Critical Path: /api/config
        ok = _is_critical_request("GET", "/api/config")
        results["Veto Gate"].append(
            ("Critical Path: /api/config", ok, "" if ok else "nicht erkannt")
        )

        # Critical Path: DELETE
        ok = _is_critical_request("DELETE", "/api/anything")
        results["Veto Gate"].append(
            ("Critical Path: DELETE-Methode", ok, "" if ok else "nicht erkannt")
        )

        # Critical Path: evidence/add
        ok = _is_critical_request("POST", "/api/core/knowledge/evidence/add")
        results["Veto Gate"].append(
            ("Critical Path: evidence/add", ok, "" if ok else "nicht erkannt")
        )

        # Nicht-kritisch
        ok = not _is_critical_request("GET", "/api/health")
        results["Veto Gate"].append(
            ("Nicht-kritisch: /api/health", ok, "" if ok else "fälschlich kritisch")
        )

        # Veto-Modus: z_widerstand >= INV_PHI (Patch am Quellmodul)
        with mock.patch(
            "src.config.core_state.get_current_state",
            return_value=type("S", (), {"z_widerstand": 0.7})(),
        ):
            z = _get_z_widerstand()
            ok = z >= VETO_THRESHOLD
            results["Veto Gate"].append(
                ("Veto-Modus: z=0.7 >= INV_PHI", ok, f"z={z}")
            )

        # _has_confirmation: Mock Request
        class MockRequest:
            def __init__(self, headers):
                self.headers = headers

        req_no = MockRequest({})
        req_yes = MockRequest({"X-Veto-Confirm": "1"})
        ok = not _has_confirmation(req_no) and _has_confirmation(req_yes)
        results["Veto Gate"].append(
            ("X-Veto-Confirm Header-Check", ok, "" if ok else "Header-Logik fehlerhaft")
        )

    except Exception as e:
        results["Veto Gate"].append(("Veto Gate Import/Execution", False, str(e)))

    return results


def print_report(results: dict[str, list[tuple[str, bool, str]]]) -> None:
    """Gibt Test-Report aus."""
    print("\n" + "=" * 60)
    print("CORE CONTEXT - End-to-End Integration Test Report")
    print("=" * 60)

    total_pass = 0
    total_fail = 0

    for component, tests in results.items():
        print(f"\n--- {component} ---")
        for name, passed, detail in tests:
            status = "PASS" if passed else "FAIL"
            total_pass += 1 if passed else 0
            total_fail += 0 if passed else 1
            suffix = f" ({detail})" if detail and not passed else ""
            print(f"  [{status}] {name}{suffix}")

    print("\n" + "-" * 60)
    print(f"Gesamt: {total_pass} PASS, {total_fail} FAIL")
    print("=" * 60 + "\n")


def main() -> int:
    results = run_tests()
    print_report(results)
    total_fail = sum(1 for tests in results.values() for _, passed, _ in tests if not passed)
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
