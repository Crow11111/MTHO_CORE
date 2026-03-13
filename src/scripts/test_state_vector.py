# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
CORE 4D State Vector – Validierung aller Schwellwerte und Konstanten.

Validiert:
- Mathematische Konstanten (PHI, INV_PHI, COMP_PHI, SYMMETRY_BREAK, BARYONIC_DELTA)
- Vordefinierte Zustaende (BASE_STATE, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN)
- Simultan-Kaskade-Zyklus-Konsistenz
- Phi-Balance- und Symmetriebruch-Pruefung
- get_current_state() mit Env-Variablen
- Drift-Veto-Override (ring0_state)
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Referenzwerte (exakte Mathematik)
PHI_EXACT = (1 + math.sqrt(5)) / 2
INV_PHI_EXACT = 1 / PHI_EXACT
COMP_PHI_EXACT = 1 - INV_PHI_EXACT


def test_constants() -> list[str]:
    """Validiert mathematische Konstanten."""
    from src.config.core_state import PHI, INV_PHI, COMP_PHI, SYMMETRY_BREAK, BARYONIC_DELTA

    errors = []
    # PHI
    if abs(PHI - PHI_EXACT) > 1e-14:
        errors.append(f"PHI: {PHI} != {PHI_EXACT}")
    else:
        print("  PHI = 1.618... OK")

    # INV_PHI = 1/PHI
    if abs(INV_PHI - INV_PHI_EXACT) > 1e-14:
        errors.append(f"INV_PHI: {INV_PHI} != {INV_PHI_EXACT}")
    else:
        print("  INV_PHI = 0.618... OK")

    # COMP_PHI = 1 - INV_PHI
    if abs(COMP_PHI - COMP_PHI_EXACT) > 1e-14:
        errors.append(f"COMP_PHI: {COMP_PHI} != {COMP_PHI_EXACT}")
    else:
        print("  COMP_PHI = 0.382... OK")

    # INV_PHI + COMP_PHI = 1
    if abs(INV_PHI + COMP_PHI - 1.0) > 1e-14:
        errors.append(f"INV_PHI + COMP_PHI != 1: {INV_PHI + COMP_PHI}")
    else:
        print("  INV_PHI + COMP_PHI = 1 OK")

    # SYMMETRY_BREAK (minimale Asymmetrie 0.49/0.51)
    if SYMMETRY_BREAK != 0.49:
        errors.append(f"SYMMETRY_BREAK: {SYMMETRY_BREAK} != 0.49")
    else:
        print("  SYMMETRY_BREAK = 0.49 OK")

    # BARYONIC_DELTA (Omega_b = 4.9% kosmologische Dichte)
    if abs(BARYONIC_DELTA - 0.049) > 1e-6:
        errors.append(f"BARYONIC_DELTA: {BARYONIC_DELTA} != 0.049")
    else:
        print("  BARYONIC_DELTA = 0.049 (Omega_b) OK")

    return errors


def test_predefined_states() -> list[str]:
    """Validiert vordefinierte Zustaende gegen CORE_4_STRANG_THEORIE."""
    from src.config.core_state import (
        BASE_STATE,
        ANSAUGEN,
        VERDICHTEN,
        ARBEITEN,
        AUSSTOSSEN,
        BARYONIC_DELTA,
        COMP_PHI,
        INV_PHI,
        SYMMETRY_BREAK,
    )

    expected = {
        "BASE_STATE": (0.49, BARYONIC_DELTA, 0.51, BARYONIC_DELTA),
        "ANSAUGEN": (COMP_PHI, BARYONIC_DELTA * 2, INV_PHI, 1 + BARYONIC_DELTA),
        "VERDICHTEN": (INV_PHI, SYMMETRY_BREAK, COMP_PHI, 2 - BARYONIC_DELTA),
        "ARBEITEN": (BARYONIC_DELTA, 0.81, BARYONIC_DELTA * 3, 3 + BARYONIC_DELTA),
        "AUSSTOSSEN": (0.49, COMP_PHI, 0.51, 4 - BARYONIC_DELTA),
    }
    states = [BASE_STATE, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN]
    names = ["BASE_STATE", "ANSAUGEN", "VERDICHTEN", "ARBEITEN", "AUSSTOSSEN"]
    errors = []

    for name, state in zip(names, states):
        exp = expected[name]
        actual = (state.x_car_cdr, state.y_gravitation, state.z_widerstand, state.w_takt)
        if not all(abs(a - e) < 1e-9 for a, e in zip(actual, exp)):
            errors.append(f"{name}: {actual} != {exp}")
        else:
            print(f"  {name}: {actual} OK")

    return errors


def test_agos_cycle() -> list[str]:
    """Prueft Simultan-Kaskade-Zyklus-Konsistenz (Takt 0-4, mit BARYONIC_DELTA-Offset)."""
    from src.config.core_state import (
        BASE_STATE,
        ANSAUGEN,
        VERDICHTEN,
        ARBEITEN,
        AUSSTOSSEN,
        BARYONIC_DELTA,
    )

    cycle = [BASE_STATE, ANSAUGEN, VERDICHTEN, ARBEITEN, AUSSTOSSEN]
    expected_w = [BARYONIC_DELTA, 1 + BARYONIC_DELTA, 2 - BARYONIC_DELTA, 3 + BARYONIC_DELTA, 4 - BARYONIC_DELTA]
    names = ["BASE_STATE(0)", "ANSAUGEN(1)", "VERDICHTEN(2)", "ARBEITEN(3)", "AUSSTOSSEN(4)"]
    errors = []

    for i, (s, exp_w, n) in enumerate(zip(cycle, expected_w, names)):
        if abs(s.w_takt - exp_w) > 1e-9:
            errors.append(f"{n}: w_takt={s.w_takt} != {exp_w}")
        else:
            print(f"  Takt {i}: {n} OK")

    return errors


def test_phi_balance() -> list[str]:
    """Prueft is_in_phi_balance()."""
    from src.config.core_state import (
        StateVector,
        INV_PHI,
        COMP_PHI,
        BASE_STATE,
        BARYONIC_DELTA,
    )

    errors = []
    # Bei INV_PHI sollte True sein
    v_inv = StateVector(INV_PHI, BARYONIC_DELTA, 0.51, BARYONIC_DELTA)
    if not v_inv.is_in_phi_balance():
        errors.append(f"x={INV_PHI} sollte phi_balance=True liefern")
    else:
        print("  is_in_phi_balance(INV_PHI) OK")

    # Bei COMP_PHI sollte True sein
    v_comp = StateVector(COMP_PHI, BARYONIC_DELTA, 0.51, BARYONIC_DELTA)
    if not v_comp.is_in_phi_balance():
        errors.append(f"x={COMP_PHI} sollte phi_balance=True liefern")
    else:
        print("  is_in_phi_balance(COMP_PHI) OK")

    # BASE_STATE (0.49) ist NICHT in Phi-Balance (Toleranz 0.05)
    if BASE_STATE.is_in_phi_balance():
        errors.append("BASE_STATE(0.49) sollte phi_balance=False liefern (neutral)")
    else:
        print("  BASE_STATE(0.49) phi_balance=False OK (neutral)")

    return errors


def test_symmetry_broken() -> list[str]:
    """Prueft is_symmetry_broken()."""
    from src.config.core_state import StateVector, SYMMETRY_BREAK, BARYONIC_DELTA

    errors = []
    # Bei y=0.49 sollte True sein
    v = StateVector(0.49, SYMMETRY_BREAK, 0.51, BARYONIC_DELTA)
    if not v.is_symmetry_broken():
        errors.append(f"y={SYMMETRY_BREAK} sollte symmetry_broken=True liefern")
    else:
        print("  is_symmetry_broken(0.49) OK")

    # Bei y nahe 0 (BARYONIC_DELTA) sollte False sein
    v0 = StateVector(0.49, BARYONIC_DELTA, 0.51, BARYONIC_DELTA)
    if v0.is_symmetry_broken():
        errors.append("y=BARYONIC_DELTA sollte symmetry_broken=False liefern")
    else:
        print("  is_symmetry_broken(BARYONIC_DELTA) False OK")

    return errors


def test_get_current_state() -> list[str]:
    """Prueft get_current_state() mit Env-Variablen."""
    from src.config.core_state import (
        get_current_state,
        BASE_STATE,
        ANSAUGEN,
        VERDICHTEN,
        ARBEITEN,
        AUSSTOSSEN,
        BARYONIC_DELTA,
        COMP_PHI,
    )

    errors = []
    orig_preset = os.environ.get("CORE_STATE_PRESET")
    orig_z = os.environ.get("CORE_Z_WIDERSTAND")

    try:
        # Default = BASE_STATE
        if "CORE_STATE_PRESET" in os.environ:
            del os.environ["CORE_STATE_PRESET"]
        if "CORE_Z_WIDERSTAND" in os.environ:
            del os.environ["CORE_Z_WIDERSTAND"]
        # Ring-0 Veto zuruecksetzen
        try:
            from src.config.ring0_state import clear_drift_veto
            clear_drift_veto()
        except Exception:
            pass

        s = get_current_state()
        if abs(s.w_takt - BASE_STATE.w_takt) > 1e-9 or abs(s.x_car_cdr - BASE_STATE.x_car_cdr) > 1e-9:
            errors.append(f"Default sollte BASE_STATE sein: {s}")
        else:
            print("  get_current_state() Default=BASE_STATE OK")

        # Preset ANSAUGEN
        os.environ["CORE_STATE_PRESET"] = "ANSAUGEN"
        s = get_current_state()
        if abs(s.w_takt - (1 + BARYONIC_DELTA)) > 1e-9 or abs(s.x_car_cdr - COMP_PHI) > 1e-9:
            errors.append(f"Preset ANSAUGEN: {s}")
        else:
            print("  CORE_STATE_PRESET=ANSAUGEN OK")

        # Preset VERDICHTEN
        os.environ["CORE_STATE_PRESET"] = "VERDICHTEN"
        s = get_current_state()
        if abs(s.w_takt - (2 - BARYONIC_DELTA)) > 1e-9:
            errors.append(f"Preset VERDICHTEN: w_takt={s.w_takt}")
        else:
            print("  CORE_STATE_PRESET=VERDICHTEN OK")

        # Z-Widerstand Override
        os.environ["CORE_STATE_PRESET"] = ""
        os.environ["CORE_Z_WIDERSTAND"] = "0.9"
        s = get_current_state()
        if abs(s.z_widerstand - 0.9) > 1e-9:
            errors.append(f"CORE_Z_WIDERSTAND=0.9: z={s.z_widerstand}")
        else:
            print("  CORE_Z_WIDERSTAND=0.9 OK")

    finally:
        if orig_preset is not None:
            os.environ["CORE_STATE_PRESET"] = orig_preset
        elif "CORE_STATE_PRESET" in os.environ:
            del os.environ["CORE_STATE_PRESET"]
        if orig_z is not None:
            os.environ["CORE_Z_WIDERSTAND"] = orig_z
        elif "CORE_Z_WIDERSTAND" in os.environ:
            del os.environ["CORE_Z_WIDERSTAND"]
        try:
            from src.config.ring0_state import clear_drift_veto
            clear_drift_veto()
        except Exception:
            pass

    return errors


def test_drift_veto_override() -> list[str]:
    """Prueft Ring-0-Veto-Override (ring0_state)."""
    from src.config.core_state import get_current_state, BASE_STATE
    from src.config.ring0_state import set_drift_veto, clear_drift_veto, get_drift_veto_override

    errors = []
    orig_preset = os.environ.get("CORE_STATE_PRESET")
    try:
        if "CORE_STATE_PRESET" in os.environ:
            del os.environ["CORE_STATE_PRESET"]
        clear_drift_veto()

        set_drift_veto(0.95)
        s = get_current_state()
        if abs(s.z_widerstand - 0.95) > 1e-9:
            errors.append(f"Drift Veto 0.95: z={s.z_widerstand}")
        else:
            print("  Drift Veto z=0.95 OK")

        clear_drift_veto()
        if get_drift_veto_override() is not None:
            errors.append("clear_drift_veto() sollte None liefern")
        else:
            print("  clear_drift_veto() OK")

    finally:
        clear_drift_veto()
        if orig_preset is not None:
            os.environ["CORE_STATE_PRESET"] = orig_preset

    return errors


def test_axiom_a5_guards() -> list[str]:
    """Axiom A5/A6: 0.0, 1.0, 0.5 muessen ValueError werfen; int muss TypeError werfen."""
    from src.config.core_state import StateVector

    errors = []
    # ValueError: 0.0
    try:
        StateVector(0.49, 0.0, 0.51, 0.049)
        errors.append("y=0.0 sollte ValueError werfen")
    except ValueError:
        print("  Axiom A5: y=0.0 -> ValueError OK")
    except Exception as e:
        errors.append(f"y=0.0: erwartet ValueError, bekam {type(e).__name__}: {e}")

    # ValueError: 1.0
    try:
        StateVector(0.49, 0.049, 1.0, 0.049)
        errors.append("z=1.0 sollte ValueError werfen")
    except ValueError:
        print("  Axiom A5: z=1.0 -> ValueError OK")
    except Exception as e:
        errors.append(f"z=1.0: erwartet ValueError, bekam {type(e).__name__}: {e}")

    # ValueError: 0.5
    try:
        StateVector(0.5, 0.049, 0.51, 0.049)
        errors.append("x=0.5 sollte ValueError werfen")
    except ValueError:
        print("  Axiom A5: x=0.5 -> ValueError OK")
    except Exception as e:
        errors.append(f"x=0.5: erwartet ValueError, bekam {type(e).__name__}: {e}")

    # TypeError: int
    try:
        StateVector(0.49, 0, 0.51, 0.049)
        errors.append("y=int sollte TypeError werfen")
    except TypeError:
        print("  Axiom A6: y=int -> TypeError OK")
    except Exception as e:
        errors.append(f"y=int: erwartet TypeError, bekam {type(e).__name__}: {e}")

    return errors


def test_magnitude() -> list[str]:
    """Prueft magnitude()."""
    from src.config.core_state import StateVector, BASE_STATE

    errors = []
    m = BASE_STATE.magnitude()
    x, y, z, w = BASE_STATE.x_car_cdr, BASE_STATE.y_gravitation, BASE_STATE.z_widerstand, BASE_STATE.w_takt
    expected = (x**2 + y**2 + z**2 + (w / 4) ** 2) ** 0.5
    if abs(m - expected) > 1e-9:
        errors.append(f"BASE_STATE.magnitude()={m} != {expected}")
    else:
        print("  BASE_STATE.magnitude() OK")

    return errors


def main() -> int:
    print("=== CORE 4D State Vector – Validierung ===\n")

    all_errors = []
    sections = [
        ("1. Mathematische Konstanten", test_constants),
        ("2. Vordefinierte Zustaende", test_predefined_states),
        ("3. Simultan-Kaskade-Zyklus", test_agos_cycle),
        ("4. Phi-Balance", test_phi_balance),
        ("5. Symmetriebruch", test_symmetry_broken),
        ("6. Axiom A5/A6 Guards", test_axiom_a5_guards),
        ("7. get_current_state()", test_get_current_state),
        ("8. Ring-0-Veto-Override", test_drift_veto_override),
        ("9. Magnitude", test_magnitude),
    ]

    for title, fn in sections:
        print(f"\n--- {title} ---")
        errs = fn()
        all_errors.extend(errs)

    print("\n" + "=" * 50)
    if all_errors:
        print("FEHLER:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print("ALLE TESTS BESTANDEN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
