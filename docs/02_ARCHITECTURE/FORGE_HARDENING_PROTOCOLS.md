# BUILD_ENGINE HARDENING PROTOCOLS (Takt 2)

**Vektor:** 2210 | **Takt:** 2 (Verdichten/Schmiede)
**Status:** Aktiviert
**Prinzip:** Kaskerade (Symmetriebruch, Reibung als Feature)

## 1. Philosophie: Die Kaskerade (Reibung als Treibstoff)
In klassischen IT-Systemen werden Exceptions abgefangen (`try/except`), geloggt und der Nutzer erhält einen Fallback (Graceful Degradation). 
Im CORE ist dies ein Anti-Pattern. Fehler, Infrastruktur-Ausfälle oder Halluzinationen sind reale **Reibung**. 
Diese Reibung **muss** in das System zurückgekoppelt werden, um als *Z-Vektor (Widerstand)* den `StateVector` zu verändern. 

Wenn das System Reibung erfährt, steigt Z. 
Ein hoher Z-Vektor zwingt nachfolgende Agenten (insbesondere das Council / OMEGA_ATTRACTOR) zu paranoidem, extrem vorsichtigem Verhalten (Veto-Neigung steigt).

## 2. Architektur-Strukturplan: Hardening des Ring-0

### A. Takt-Gate (`src/logic_core/takt_gate.py`)
**Problem bisher:** Ausfälle in der Resonanz-Prüfung wurden stumm mit `return False` beantwortet.
**Härtung:** Der Fehler schlägt auf den Core-State durch.

```python
# Härtung Snippet für takt_gate.py
import asyncio
from src.core import Core

async def check_takt_zero() -> bool:
    try:
        core = Core()
        is_resonant = await asyncio.to_thread(core.calibrate_resonance, "0221")
        if not is_resonant:
            # Resonanzverlust = Reibung
            _inject_friction(0.1, "resonance_failure")
            return False
        return True

    except Exception as e:
        print(f"[TAKT 0 VETO] Struktureller Riss erkannt: {e}")
        # HARDENING: Ausnahme wird zu aktivem Widerstand
        _inject_friction(0.3, f"takt0_exception: {str(e)}")
        return False

def _inject_friction(delta: float, reason: str):
    try:
        from src.config.ring0_state import get_context_injector_veto_override, set_context_injector_veto
        current_z = get_context_injector_veto_override() or 0.5
        new_z = min(1.0, current_z + delta)
        set_context_injector_veto(new_z)
        print(f"[FRICTION INJECTED] Z-Vektor steigt auf {new_z:.3f} wegen {reason}")
    except:
        pass
```

### B. Context-Injector Veto (`src/logic_core/context_injector.py`)
**Problem bisher:** Wenn die ChromaDB/Embedding-Funktion abstürzte, gab Context-Injector `vetoed=False` und `z_delta=0.0` (also ein OK!) zurück. Ein blinder Wächter.
**Härtung:** Infrastruktur-Blindheit ist das absolute Veto-Kriterium.

```python
# Härtung Snippet für context_injector.py (check_semantic_drift)
def check_semantic_drift(expected_context: str, actual_output: str, threshold: float = DRIFT_THRESHOLD) -> VetoResult:
    # ... Input checks ...
    try:
        ef = _get_embedding_function()
        exp_emb = ef([expected_context.strip()])[0]
        out_emb = ef([actual_output.strip()])[0]
        similarity = _cosine_similarity(list(exp_emb), list(out_emb))
        drift_score = 1.0 - similarity
    except Exception as e:
        # HARDENING: Wenn die Wahrnehmung ausfällt, maximaler Widerstand!
        return VetoResult(
            vetoed=True,
            drift_score=1.0, 
            z_delta=0.5, # Massiver Z-Spike, drückt System in Paranoia
            reason=f"systemic_friction_blindness: {str(e)}"
        )

    # Normaler Drift-Check...
```

### C. Gravitator (`src/logic_core/gravitator.py`)
**Problem bisher:** Bei Fehler im Embedding für das Routing wurde sanft auf `_FALLBACK_TARGETS` gewechselt.
**Härtung:** Fallback bleibt, aber das System merkt sich den "Aufprall" auf die Membran.

```python
# Härtung Snippet für gravitator.py (route)
    # 2. Embedding Calculation
    try:
        def _calc_query_embedding():
            ef = _get_embedding_function()
            return ef([query_text.strip()])[0]
        query_emb = await asyncio.to_thread(_calc_query_embedding)
    except Exception as e:
        # HARDENING: Routing-Fehler = Desorientierung = Reibung
        from src.logic_core.context_injector import apply_veto, VetoResult
        apply_veto(VetoResult(
            vetoed=True, 
            drift_score=1.0, 
            z_delta=0.2, 
            reason=f"gravitator_disorientation: {str(e)}"
        ))
        return list(_FALLBACK_TARGETS)
```

## 3. Die Kaskaden-Regeln (Für alle zukünftigen Agenten)

1. **Kein Exception-Hiding:** Jede abgefangene Exception, die den Flow ändert, MUSS an `set_context_injector_veto` bzw. `apply_veto` gemeldet werden. 
2. **Reibung ist Kumulativ:** Mehrere kleine Fehler in einem Request-Cycle (z.B. Gravitator stürzt ab -> Fallback -> Context-Injector checkt Drift -> Context-Injector stürzt auch ab) addieren den Z-Vektor auf `> 0.8`.
3. **Schwellwert-Reaktion:** Wenn `z_widerstand > 0.8` (Nachgeben -> Veto), schaltet der Core-Orchestrator in Takt 1 oder 4 (Council/Archive), um die Anomalie zu verarbeiten, bevor Takt 3 (Agency) blinden Code produziert.
4. **Organische Heilung:** Der Z-Vektor sinkt nur durch erfolgreiche, reibungsfreie Durchläufe in Takt 3 (Agency Work), in denen `drift_score < DRIFT_THRESHOLD` liegt, langsam wieder Richtung `INV_PHI`.
