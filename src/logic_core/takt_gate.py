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
        from src.logic_core.crystal_grid_engine import CrystalGridEngine

        z_vector = float(os.getenv("CORE_Z_WIDERSTAND", "0.049"))
        if z_vector >= 0.9:
            print(f"[TAKT 0 VETO] System Locked - Z-Vector Critical ({z_vector}). Auto-Loop detected.")
            return False

        # Takt 0 Baryonic Check (Gitter-Validierung)
        # Snapping-Pruefung fuer Λ (0.049)
        resonance = CrystalGridEngine.apply_operator_query(z_vector)
        if resonance < 0.049:
            print(f"[TAKT 0 VETO] Baryonic Limit Breach: {resonance} < 0.049")
            return False

        # Takt 0 is idle state (Silence/Potential).
        # We ensure we are not in a 'COLLAPSED' state (y=1 without purpose).
        # (Simplified check for now)
        return True

    except Exception as e:
        print(f"[TAKT 0 VETO] Gate Check Exception: {e}")
        return False
