# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
MTHO 4D State Vector - Komprimierte Systemzustand-Repraesentation.

Dieser Vektor ist der "Bootloader" - er enthaelt den gesamten Systemkontext
in einer Form die direkt als Embedding/Query verwendet werden kann.

Dimensionen:
    X: CAR/CDR Balance (Δ..1-Δ, Skala NT↔ND)
    Y: Gravitation (Δ=Basis/flat, 1-Δ=Kollaps)
    Z: Widerstand (Δ=Nachgeben, 1-Δ=Veto)
    W: Takt (Δ-offset pro Stufe, NICHT ganzzahlig)
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import math
import os

# Import MTHO Core Definitions as Single Source of Truth
# CRITICAL: Hard dependency on MTHO Core. System fails if not present.
from src.mtho_core import (
    M_VALUE, T_VALUE, H_VALUE, O_VALUE,
    BARYONIC_LIMIT, MTHO_LEGACY_MAP
)

# Mathematische Konstanten (aus engine_patterns.py)
PHI = 1.6180339887498948482
INV_PHI = 0.6180339887498948482
COMP_PHI = 0.3819660112501051518
SYMMETRY_BREAK = 0.49
BARYONIC_DELTA = BARYONIC_LIMIT


@dataclass
class MTHOStateVector:
    """4D Zustandsvektor des MTHO-Systems."""

    x_car_cdr: float  # Δ=NT-Pol, 1-Δ=ND-Pol
    y_gravitation: float  # Δ=Basis/flat, 1-Δ=Kollaps
    z_widerstand: float  # Δ=Nachgeben, 1-Δ=Veto
    w_takt: float  # 0-4 Simultan-Kaskade-Zyklus (jetzt float wg. asymmetrischem Offset)

    def __post_init__(self):
        """Axiom A1 + A6 Enforcement: Verbotene Werte zur Laufzeit abfangen."""
        for name, val in [
            ("x_car_cdr", self.x_car_cdr),
            ("y_gravitation", self.y_gravitation),
            ("z_widerstand", self.z_widerstand),
            ("w_takt", self.w_takt),
        ]:
            if not isinstance(val, float):
                raise TypeError(
                    f"[AXIOM-A6] {name} muss float sein, ist {type(val).__name__}. "
                    f"int ist in der Resonanz-Domaene verboten."
                )
            if val == 0.0:
                raise ValueError(
                    f"[AXIOM-A1] {name}=0.0 verletzt das 0=0-Verbot. "
                    f"Minimum: BARYONIC_DELTA ({BARYONIC_DELTA})"
                )
            if val == 1.0:
                raise ValueError(
                    f"[AXIOM-A1] {name}=1.0 verletzt das Einheits-Verbot. "
                    f"Maximum: 1.0 - BARYONIC_DELTA ({1.0 - BARYONIC_DELTA})"
                )
            if val == 0.5:
                raise ValueError(
                    f"[AXIOM-A1] {name}=0.5 verletzt das Symmetrie-Verbot. "
                    f"Verwende SYMMETRY_BREAK ({SYMMETRY_BREAK}) oder 0.51."
                )

    def to_tuple(self) -> Tuple[float, float, float, float]:
        return (self.x_car_cdr, self.y_gravitation, self.z_widerstand, float(self.w_takt))

    def magnitude(self) -> float:
        return math.sqrt(
            self.x_car_cdr**2
            + self.y_gravitation**2
            + self.z_widerstand**2
            + (self.w_takt / 4) ** 2
        )

    def is_in_phi_balance(self) -> bool:
        """Prueft ob der Vektor im Phi-Gleichgewicht ist."""
        return abs(self.x_car_cdr - INV_PHI) < 0.05 or abs(self.x_car_cdr - COMP_PHI) < 0.05

    def is_symmetry_broken(self) -> bool:
        """Prueft ob der minimale Symmetriebruch aktiv ist."""
        return abs(self.y_gravitation - SYMMETRY_BREAK) < 0.02


# Vordefinierte Zustaende (mit asymmetrischem Offset, kein 0=0)
BASE_STATE = MTHOStateVector(x_car_cdr=0.49, y_gravitation=BARYONIC_DELTA, z_widerstand=0.51, w_takt=BARYONIC_DELTA)
ANSAUGEN = MTHOStateVector(x_car_cdr=COMP_PHI, y_gravitation=BARYONIC_DELTA*2, z_widerstand=INV_PHI, w_takt=1 + BARYONIC_DELTA)
VERDICHTEN = MTHOStateVector(x_car_cdr=INV_PHI, y_gravitation=SYMMETRY_BREAK, z_widerstand=COMP_PHI, w_takt=2 - BARYONIC_DELTA)
ARBEITEN = MTHOStateVector(x_car_cdr=BARYONIC_DELTA, y_gravitation=0.81, z_widerstand=BARYONIC_DELTA*3, w_takt=3 + BARYONIC_DELTA)
AUSSTOSSEN = MTHOStateVector(x_car_cdr=0.49, y_gravitation=COMP_PHI, z_widerstand=0.51, w_takt=4 - BARYONIC_DELTA)


# ---------------------------------------------------------------------------
# MTHO Bases (DNA der Realitaet)
# ---------------------------------------------------------------------------
MTHO_BASES = {
    "M": {"name": "ExecutionRuntime", "dna": "T", "val": M_VALUE, "role": "Physik/Feuer", "legacy": "P"},
    "T": {"name": "LogicFlow", "dna": "A", "val": T_VALUE, "role": "Info/Fluss", "legacy": "I"},
    "H": {"name": "StateAnchor", "dna": "G", "val": H_VALUE, "role": "Struktur/Erde", "legacy": "S"},
    "O": {"name": "ConstraintValidator", "dna": "C", "val": O_VALUE, "role": "Logik/Luft", "legacy": "L"},
}

MTHO_PAIRINGS = {
    "M": "H",  # Symmetrisches Rückgrat
    "H": "M",
    "O": "T",  # Asymmetrischer Motor
    "T": "O",
}

# 4-Strang Architektur (Updated to MTHO)
TETRALOGIE = {
    "EXECUTION": {"takt": 3, "mtho": "M", "car": "Effizienz", "cdr": "Clean Code"},
    "ORCHESTRATOR": {"takt": [1, 4], "mtho": "O", "car": "Paranoia", "cdr": "Compliance"},
    "ARCHITECTURE": {"takt": 2, "mtho": "T", "car": "Chaos", "cdr": "Architektur-Spec"},
    "ANCHOR": {"takt": 4, "mtho": "H", "car": "Vektor-Cluster", "cdr": "SQL-Index"},
}


# Simulation Evidence Statistik (aus ChromaDB VPS Export)
# Updated to reflect MTHO distribution logic if needed, kept generic for now
SIMULATION_EVIDENCE_STATS = {
    "vektoren": 12,
    "indizien": 58,
    "max_aeste": 13,
    "mtho_verteilung": {"O": 19, "M": 13, "T": 13, "H": 13}, # New keys
    "chargaff_li": 32,
    "chargaff_sp": 26,
    "phi_delta": BARYONIC_DELTA,
}


def get_current_state() -> MTHOStateVector:
    """Gibt den aktuellen Systemzustand zurueck (Default: BASE_STATE).
    Dynamisch aus Umgebung: MTHO_Z_WIDERSTAND, MTHO_STATE_PRESET.
    Ring-0 Veto: ring0_state Override hat Vorrang (Ring-0 Core Stability Anchor).
    """

    # Ring-0 Veto Override
    try:
        from src.config.ring0_state import get_drift_veto_override

        z_override = get_drift_veto_override()
        if z_override is not None:
            z_clamped = max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z_override))
            return MTHOStateVector(
                x_car_cdr=BASE_STATE.x_car_cdr,
                y_gravitation=BASE_STATE.y_gravitation,
                z_widerstand=z_clamped,
                w_takt=BASE_STATE.w_takt,
            )
    except Exception:
        pass

    preset = os.getenv("MTHO_STATE_PRESET", "").strip().upper()
    if preset == "ANSAUGEN":
        return ANSAUGEN
    if preset == "VERDICHTEN":
        return VERDICHTEN
    if preset == "ARBEITEN":
        return ARBEITEN
    if preset == "AUSSTOSSEN":
        return AUSSTOSSEN
    z_raw = os.getenv("MTHO_Z_WIDERSTAND", "")
    if z_raw:
        try:
            z = float(z_raw)
            return MTHOStateVector(
                x_car_cdr=BASE_STATE.x_car_cdr,
                y_gravitation=BASE_STATE.y_gravitation,
                z_widerstand=max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z)),
                w_takt=BASE_STATE.w_takt,
            )
        except ValueError:
            pass
    return BASE_STATE


def state_to_embedding_text() -> str:
    """Generiert einen Text der als Embedding-Query verwendet werden kann.
    Updated for MTHO Native format.
    """
    return f"""MTHO 4D State Vector - Bootloader (MTHO Native)
Tetralogie: Execution(M/P)-Orchestrator(O/L)-Architecture(T/I)-Anchor(H/S)
Simultan-Kaskade-Zyklus: Diagnose(0)->Ansaugen(1)->Verdichten(2)->Arbeiten(3)->Ausstossen(4)
CAR/CDR: ND-Kern(Tiefe,Muster,Divergenz) / NT-Interface(API,Docs,Clean)
Gravitation: flat->Attraktor(Kollaps), Schwellwert={INV_PHI:.3f}
MTHO: M(ExecutionRuntime,Physik), T(LogicFlow,Info), H(StateAnchor,Struktur), O(ConstraintValidator,Logik)
DNA: M(T), T(A), H(G), O(C)
Pairings: M-H (Symmetrisches Rueckgrat), O-T (Asymmetrischer Motor)
Symmetriebruch: {SYMMETRY_BREAK}, Baryonisches Delta: {BARYONIC_DELTA}
Evidence: {SIMULATION_EVIDENCE_STATS['indizien']} Indizien, {SIMULATION_EVIDENCE_STATS['vektoren']} Vektoren
"""
