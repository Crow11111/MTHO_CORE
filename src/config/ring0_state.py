# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Ring-0 Mutable State – z_widerstand Override durch Drift Veto.

Drift Veto kann z_widerstand erhöhen; get_current_state() liest diesen Override.
"""
from __future__ import annotations

import inspect
import os

from src.config.core_state import BARYONIC_DELTA

_z_widerstand_override: float | None = None

ALLOWED_RING0_CALLERS = {
    "z_vector_damper",
    "context_injector",
    "takt_gate",
    "agos_zero_watchdog",
    "main",
    "test_state_vector",
    "ring0_state",
}


def _verify_caller() -> None:
    """Prueft ob der aufrufende Code ein berechtigtes Modul ist."""
    frame = inspect.stack()[2]
    module = os.path.basename(frame.filename).replace(".py", "")
    if module not in ALLOWED_RING0_CALLERS:
        raise PermissionError(
            f"[RING-0] Unerlaubter Zugriff auf State von '{module}'. "
            f"Erlaubt: {ALLOWED_RING0_CALLERS}"
        )


def set_drift_veto(z: float) -> None:
    """Setzt z_widerstand-Override (Δ..1-Δ). Wird von get_current_state() verwendet."""
    _verify_caller()
    global _z_widerstand_override
    _z_widerstand_override = max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z))


def clear_drift_veto() -> None:
    """Entfernt Drift-Veto-Override."""
    _verify_caller()
    global _z_widerstand_override
    _z_widerstand_override = None


def get_drift_veto_override() -> float | None:
    """Liefert aktuellen z_widerstand-Override oder None."""
    return _z_widerstand_override


# Backward-Kompatibilitaet
set_context_veto = set_drift_veto
clear_context_veto = clear_drift_veto
get_context_veto_override = get_drift_veto_override
