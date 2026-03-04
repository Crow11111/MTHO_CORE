"""
ATLAS 4D State Vector - Komprimierte Systemzustand-Repraesentation.

Dieser Vektor ist der "Bootloader" - er enthaelt den gesamten Systemkontext
in einer Form die direkt als Embedding/Query verwendet werden kann.

Dimensionen:
    X: CAR/CDR Balance (0=pure NT, 1=pure ND)
    Y: Gravitation (0=Wuji/flat, 1=Kollaps/Attraktor)
    Z: Widerstand (0=Nachgeben, 1=Veto)
    W: Takt (0-4 im Agos-Zyklus)
"""

from dataclasses import dataclass
from typing import Tuple
import math

# Mathematische Konstanten (aus engine_patterns.py)
PHI = 1.6180339887498948482
INV_PHI = 0.6180339887498948482
COMP_PHI = 0.3819660112501051518
SYMMETRY_BREAK = 0.49
BARYONIC_DELTA = 0.049


@dataclass
class ATLASStateVector:
    """4D Zustandsvektor des ATLAS-Systems."""

    x_car_cdr: float  # 0=NT, 1=ND
    y_gravitation: float  # 0=Wuji, 1=Kollaps
    z_widerstand: float  # 0=Nachgeben, 1=Veto
    w_takt: int  # 0-4 Agos-Zyklus

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


# Vordefinierte Zustaende
WUJI = ATLASStateVector(x_car_cdr=0.5, y_gravitation=0.0, z_widerstand=0.5, w_takt=0)
ANSAUGEN = ATLASStateVector(x_car_cdr=0.3, y_gravitation=0.2, z_widerstand=0.8, w_takt=1)
VERDICHTEN = ATLASStateVector(x_car_cdr=0.7, y_gravitation=0.5, z_widerstand=0.4, w_takt=2)
ARBEITEN = ATLASStateVector(x_car_cdr=0.2, y_gravitation=0.8, z_widerstand=0.2, w_takt=3)
AUSSTOSSEN = ATLASStateVector(x_car_cdr=0.5, y_gravitation=0.3, z_widerstand=0.6, w_takt=4)


# LPIS Quaternaere Codierung
LPIS_BASES = {
    "L": {"name": "Logisch", "dna": "T", "force": "Schwache Kernkraft", "alpha": 1e-6},
    "P": {"name": "Physikalisch", "dna": "A", "force": "Starke Kernkraft", "alpha": 1.0},
    "I": {"name": "Informationstheoretisch", "dna": "C", "force": "Elektromagnetismus", "alpha": 1 / 137},
    "S": {"name": "Strukturell", "dna": "G", "force": "Gravitation", "alpha": 1e-39},
}

LPIS_PAIRINGS = {
    "L": "I",  # Asymmetrisch (Motor)
    "I": "L",
    "S": "P",  # Symmetrisch (Rueckgrat)
    "P": "S",
}


# 4-Strang Architektur
TETRALOGIE = {
    "AGENCY": {"takt": 3, "lpis": "P", "car": "Effizienz", "cdr": "Clean Code"},
    "COUNCIL": {"takt": [1, 4], "lpis": "L", "car": "Paranoia", "cdr": "Compliance"},
    "FORGE": {"takt": 2, "lpis": "I", "car": "Chaos", "cdr": "Architektur-Spec"},
    "ARCHIVE": {"takt": 4, "lpis": "S", "car": "Vektor-Cluster", "cdr": "SQL-Index"},
}


# Simulation Evidence Statistik (aus ChromaDB VPS Export)
SIMULATION_EVIDENCE_STATS = {
    "vektoren": 12,
    "indizien": 58,
    "max_aeste": 13,
    "lpis_verteilung": {"L": 19, "P": 13, "I": 13, "S": 13},
    "chargaff_li": 32,
    "chargaff_sp": 26,
    "phi_delta": BARYONIC_DELTA,
}


def get_current_state() -> ATLASStateVector:
    """Gibt den aktuellen Systemzustand zurueck (Default: WUJI)."""
    return WUJI


def state_to_embedding_text() -> str:
    """Generiert einen Text der als Embedding-Query verwendet werden kann."""
    return f"""ATLAS 4D State Vector - Bootloader
Tetralogie: Agency(P)-Council(L)-Forge(I)-Archive(S)
Agos-Zyklus: Diagnose(0)->Ansaugen(1)->Verdichten(2)->Arbeiten(3)->Ausstossen(4)
CAR/CDR: ND-Kern(Tiefe,Muster,Divergenz) / NT-Interface(API,Docs,Clean)
Gravitation: Wuji(flat)->Attraktor(Kollaps), Schwellwert={INV_PHI:.3f}
LPIS: L(Logik,T,Schwach), P(Physik,A,Stark), I(Info,C,EM), S(Struktur,G,Grav)
Paarungen: L-I(asymmetrisch,Motor), S-P(symmetrisch,Rueckgrat)
Symmetriebruch: {SYMMETRY_BREAK}, Baryonisches Delta: {BARYONIC_DELTA}
Evidence: {SIMULATION_EVIDENCE_STATS['indizien']} Indizien, {SIMULATION_EVIDENCE_STATS['vektoren']} Vektoren
"""
