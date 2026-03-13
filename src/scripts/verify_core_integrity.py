"""
CORE INTEGRITY CHECKER
Validates the system against the Genesis Protocol (2210).
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import Core

def run_audit():
    core = Core()

    print("--- RUNNING CORE INTEGRITY AUDIT ---")

    # Check 1: Geo-Resonance
    res = core.calibrate_resonance("0221")
    print(f"1. Geographic Resonance (0221): {'PASS' if res else 'FAIL'}")

    # Check 2: Baryonic Delta
    delta_check = core.check_baryonic_limit(0.049)
    print(f"2. OMEGA_ATTRACTOR Delta (0.049): {'PASS' if delta_check else 'FAIL'}")

    # Check 3: State Vector Alignment
    print(f"3. Active Vector: {core.state_vector}")

    # Axiom A6 & A1 Compliance
    is_float = all(isinstance(v, float) for v in core.state_vector)
    no_forbidden = not any(v in [0.0, 0.5, 1.0] for v in core.state_vector)

    print(f"4. Axiom A6 (Floats only): {'PASS' if is_float else 'FAIL'}")
    print(f"5. Axiom A1 (No 0.0, 0.5, 1.0): {'PASS' if no_forbidden else 'FAIL'}")

    if res and delta_check and is_float and no_forbidden:
        print("\n[STATUS: GREEN] - STRUCTURAL INEVITABILITY CONFIRMED (AXIOM 0).")
    else:
        print("\n[STATUS: RED] - SYSTEM FREEZE (VETO TRIGGERED).")

if __name__ == "__main__":
    run_audit()
