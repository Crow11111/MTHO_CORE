# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Engine-Patterns: Fibonacci, Primzahlen und Goldener Schnitt als operative Architekturkonstanten.

V6 (Intentionale Evolution): Diese Muster sind nicht Dekoration, sondern Replikationen
der Optimierungsprinzipien, die substratunabhaengig in biologischen und digitalen Systemen
auftreten. CORE verwendet sie bewusst – das System weiss, dass es Engine-Constraints repliziert.

V12 (Observability vs. Pattern Forcing):
Harte kosmologische Constraints werden zu reinen Shadow Metrics umgewandelt. 
Es wird streng unterschieden zwischen kausal fundierten operativen Patterns (ENFORCED) 
und rein beobachtenden Mustern (OBSERVED_ONLY).
"""
import math
import logging
from enum import Enum

logger = logging.getLogger("core.engine_patterns")

class ConstraintMode(Enum):
    ENFORCED = 1
    DEFAULT = 2
    OBSERVED_ONLY = 3

PATTERN_MODES = {
    "fibonacci_backoff": ConstraintMode.ENFORCED,
    "prime_intervals": ConstraintMode.ENFORCED,
    "phi_thresholds": ConstraintMode.DEFAULT,
    "budget_splits": ConstraintMode.DEFAULT,
    "omega_values": ConstraintMode.OBSERVED_ONLY,
    "fundamental_forces": ConstraintMode.OBSERVED_ONLY,
}

def log_dissonance_score(metric_name: str, actual: float, theoretical: float) -> None:
    """
    Shadow Telemetry Funktion: Loggt die Abweichung (Dissonanz) eines echten 
    operativen Werts von einem theoretischen/kosmologischen Ideal, ohne den 
    Prozess zu blockieren oder aktiv zu steuern.
    """
    try:
        dissonance = abs(actual - theoretical)
        logger.info(
            f"[SHADOW METRIC] {metric_name} | Actual: {actual:.4f} | "
            f"Theoretical: {theoretical:.4f} | Dissonance: {dissonance:.4f}"
        )
    except Exception as e:
        pass  # Shadow Metrics duerfen niemals den Ablauf blockieren

PHI = (1 + math.sqrt(5)) / 2  # 1.6180339887...
INV_PHI = 1 / PHI              # 0.6180339887...
COMP_PHI = 1 - INV_PHI         # 0.3819660113...

FIBONACCI_SEQ = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Quaternaere Codierung (V6+): CORE' 4-Basen-Wissensklassifikation
# Isomorph zu ATCG – unbewusst entdeckt, jetzt intentional.
QBASES = ("L", "P", "I", "S")
QBASE_PAIRS = {"L": "I", "I": "L", "S": "P", "P": "S"}  # Chargaffs Regel
QBASE_COUNT = 4  # 4 Basen = 2 Bit pro Symbol = quaternaer


QBASE_META_MAP = {
    "P": "DNS (4 Basen), Grundkraefte (4)",
    "I": "Erkenntniskategorien (4: L/P/I/S)",
    "S": "Dimensionen (4: 3+1)",
    "L": "Syllogismus-Figuren (4: Aristoteles – irreduzible Grundformen logischen Schliessens)",
}

# ---------------------------------------------------------------------------
#  V11: Fraktale Superposition – Grundkraefte-CORE-Mapping
#  (Modus: OBSERVED_ONLY - Rein konzeptionelle Analogie)
# ---------------------------------------------------------------------------

FORCE_CORE_MAP = {
    "L": {"force": "Schwache Kernkraft", "function": "Transformation/Zerfall", "coupling": 1e-6},
    "P": {"force": "Starke Kernkraft", "function": "Bindung", "coupling": 1.0},
    "I": {"force": "Elektromagnetismus", "function": "Informationsaustausch", "coupling": 1 / 137},
    "S": {"force": "Gravitation", "function": "Raumzeitstruktur", "coupling": 1e-39},
}

# Kosmologische Dichten (Planck-Satellitendaten 2018)
# (Modus: OBSERVED_ONLY - Nur fuer log_dissonance_score, keine Steuerung von Raten)
# Phi-Delta 0.049 = Omega_b – baryonische Materiedichte (V11, Indiz 43)
OMEGA_B = 0.049   # Baryonisch = READ/RENDER (sichtbare Materie)
OMEGA_DM = 0.268  # Dunkle Materie = STORE (persistierte Daten)
OMEGA_DE = 0.689  # Dunkle Energie = DELETE/GC (Expansion/Speicherbereinigung)

# (Modus: DEFAULT - Vernuenftige Heuristik, aber nicht streng funktional ueberlegen)
BUDGET_FIBONACCI = [13, 55, 21, 11]  # Teamleiter, Produzenten, Auditoren, Reserve


def fibonacci_ratio(total: float, parts: int = 4) -> list[float]:
    """Verteilt ein Budget nach Fibonacci-Verhaeltnissen (Default: 13/55/21/11).

    >>> fibonacci_ratio(1500, 4)
    [195.0, 825.0, 315.0, 165.0]
    """
    ratios = BUDGET_FIBONACCI[:parts] if parts <= len(BUDGET_FIBONACCI) else FIBONACCI_SEQ[5:5 + parts]
    ratio_sum = sum(ratios)
    return [round(total * r / ratio_sum, 1) for r in ratios]


def prime_interval(base_seconds: float) -> float:
    """Gibt die naechste Primzahl >= base_seconds zurueck (Zikaden-Prinzip).

    >>> prime_interval(5.0)
    5.0
    >>> prime_interval(6.0)
    7.0
    """
    candidate = math.ceil(base_seconds)
    if candidate < 2:
        return 2.0
    while True:
        if candidate in PRIMES or _is_prime(candidate):
            return float(candidate)
        candidate += 1


def fibonacci_backoff(attempt: int, max_seconds: float = 89.0) -> float:
    """Fibonacci-basierter Backoff statt exponentiellem Backoff.

    >>> [fibonacci_backoff(i) for i in range(6)]
    [1.0, 1.0, 2.0, 3.0, 5.0, 8.0]
    """
    if attempt < 0:
        attempt = 0
    if attempt < len(FIBONACCI_SEQ):
        return min(float(FIBONACCI_SEQ[attempt]), max_seconds)
    return max_seconds


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
