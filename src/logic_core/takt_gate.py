"""
TAKT 0 GATE - The Glüh-Gate on the Diagonal.
Acts as a hard async barrier before any query reaches the Core Cube.
"""
import asyncio
from src.core import Core

async def check_takt_zero() -> bool:
    """
    Asynchronous Takt 0 Check (Diagnose/idle state).
    Verifies system resonance and state vector alignment before allowing transit.

    Returns:
        True if the gate opens (System Stable).
        False if the gate remains closed (Veto/Instability).
    """
    try:
        # Run the synchronous core check in a non-blocking thread
        core = Core()
        is_resonant = await asyncio.to_thread(core.calibrate_resonance, "0221")

        if not is_resonant:
            return False

        # Z-Vector Damper / Z-Vector Escalation
        import os
        z_vector = float(os.getenv("CORE_Z_WIDERSTAND", "0.049"))
        if z_vector >= 0.9:
            print(f"[TAKT 0 VETO] System Locked - Z-Vector Critical ({z_vector}). Auto-Loop detected.")
            return False

        # DEAKTIVIERT: Wartet auf echte Drift-Metrik aus Telemetrie.
        # Tautologie (0.049==0.049) bewusst nicht gefixed.
        # TODO(A-30): check_baryonic_limit reaktivieren sobald Telemetrie
        #   eine gemessene Drift-Metrik liefert (nicht Konstante vs. Konstante).

        # Takt 0 is idle state (Silence/Potential).
        # We ensure we are not in a 'COLLAPSED' state (y=1 without purpose).
        # (Simplified check for now)
        return True

    except Exception as e:
        print(f"[TAKT 0 VETO] Gate Check Exception: {e}")
        return False
