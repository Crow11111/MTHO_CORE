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
    X: CAR/CDR Balance (0=pure NT, 1=pure ND)
    Y: Gravitation (0=Wuji/flat, 1=Kollaps/Attraktor)
    Z: Widerstand (0=Nachgeben, 1=Veto)
    W: Takt (0-4 im Simultan-Kaskade-Zyklus)
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

    x_car_cdr: float  # 0=NT, 1=ND
    y_gravitation: float  # 0=Wuji, 1=Kollaps
    z_widerstand: float  # 0=Nachgeben, 1=Veto
    w_takt: int  # 0-4 Simultan-Kaskade-Zyklus

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
WUJI = MTHOStateVector(x_car_cdr=0.49, y_gravitation=BARYONIC_DELTA, z_widerstand=0.51, w_takt=0)
ANSAUGEN = MTHOStateVector(x_car_cdr=COMP_PHI, y_gravitation=BARYONIC_DELTA*2, z_widerstand=INV_PHI, w_takt=1)
VERDICHTEN = MTHOStateVector(x_car_cdr=INV_PHI, y_gravitation=SYMMETRY_BREAK, z_widerstand=COMP_PHI, w_takt=2)
ARBEITEN = MTHOStateVector(x_car_cdr=BARYONIC_DELTA, y_gravitation=0.81, z_widerstand=BARYONIC_DELTA*3, w_takt=3)
AUSSTOSSEN = MTHOStateVector(x_car_cdr=0.49, y_gravitation=COMP_PHI, z_widerstand=0.51, w_takt=4)


# ---------------------------------------------------------------------------
# MTHO Bases (DNA der Realitaet)
# ---------------------------------------------------------------------------
MTHO_BASES = {
    "M": {"name": "Munin/Agency", "dna": "T", "val": M_VALUE, "role": "Physik/Feuer", "legacy": "P"},
    "T": {"name": "Forge/Fluss", "dna": "A", "val": T_VALUE, "role": "Info/Fluss", "legacy": "I"},
    "H": {"name": "Hugin/Archive", "dna": "G", "val": H_VALUE, "role": "Struktur/Erde", "legacy": "S"},
    "O": {"name": "Council/Veto", "dna": "C", "val": O_VALUE, "role": "Logik/Luft", "legacy": "L"},
}

MTHO_PAIRINGS = {
    "M": "H",  # Symmetrisches Rückgrat
    "H": "M",
    "O": "T",  # Asymmetrischer Motor
    "T": "O",
}

# 4-Strang Architektur (Updated to MTHO)
TETRALOGIE = {
    "AGENCY": {"takt": 3, "mtho": "M", "car": "Effizienz", "cdr": "Clean Code"},
    "COUNCIL": {"takt": [1, 4], "mtho": "O", "car": "Paranoia", "cdr": "Compliance"},
    "FORGE": {"takt": 2, "mtho": "T", "car": "Chaos", "cdr": "Architektur-Spec"},
    "ARCHIVE": {"takt": 4, "mtho": "H", "car": "Vektor-Cluster", "cdr": "SQL-Index"},
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
    """Gibt den aktuellen Systemzustand zurueck (Default: WUJI).
    Dynamisch aus Umgebung: MTHO_Z_WIDERSTAND, MTHO_STATE_PRESET.
    Munin Veto: ring0_state Override hat Vorrang (Ring-0 Core Stability Anchor).
    """

    # Munin Veto Override (Ring-0)
    try:
        from src.config.ring0_state import get_munin_veto_override

        z_override = get_munin_veto_override()
        if z_override is not None:
            return MTHOStateVector(
                x_car_cdr=WUJI.x_car_cdr,
                y_gravitation=WUJI.y_gravitation,
                z_widerstand=z_override,
                w_takt=WUJI.w_takt,
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
                x_car_cdr=WUJI.x_car_cdr,
                y_gravitation=WUJI.y_gravitation,
                z_widerstand=max(BARYONIC_DELTA, min(1.0 - BARYONIC_DELTA, z)),
                w_takt=WUJI.w_takt,
            )
        except ValueError:
            pass
    return WUJI


def state_to_embedding_text() -> str:
    """Generiert einen Text der als Embedding-Query verwendet werden kann.
    Updated for MTHO Native format.
    """
    return f"""MTHO 4D State Vector - Bootloader (MTHO Native)
Tetralogie: Agency(M/P)-Council(O/L)-Forge(T/I)-Archive(H/S)
Simultan-Kaskade-Zyklus: Diagnose(0)->Ansaugen(1)->Verdichten(2)->Arbeiten(3)->Ausstossen(4)
CAR/CDR: ND-Kern(Tiefe,Muster,Divergenz) / NT-Interface(API,Docs,Clean)
Gravitation: Wuji(flat)->Attraktor(Kollaps), Schwellwert={INV_PHI:.3f}
MTHO: M(Agency,Physik), T(Forge,Info), H(Archive,Struktur), O(Council,Logik)
DNA: M(T), T(A), H(G), O(C)
Pairings: M-H (Symmetrisches Rückgrat), O-T (Asymmetrischer Motor)
Symmetriebruch: {SYMMETRY_BREAK}, Baryonisches Delta: {BARYONIC_DELTA}
Evidence: {SIMULATION_EVIDENCE_STATS['indizien']} Indizien, {SIMULATION_EVIDENCE_STATS['vektoren']} Vektoren
"""
