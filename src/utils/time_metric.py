import time
import random
import math
from loguru import logger
from src.config.core_state import get_current_state, BARYONIC_DELTA
import asyncio

def get_friction_timeout(base_timeout: float) -> float:
    """
    Dynamische Raum-Zeit-Metrik für Timeouts.
    Dehnt den Timeout basierend auf dem aktuellen System-Widerstand (Z-Vektor) aus.
    """
    try:
        state = get_current_state()
        # Die Reibung dehnt den Timeout aus.
        # Bei Z hoch erhöht sich der Timeout asymmetrisch.
        friction_multiplier = 1.0 + (state.z_widerstand * BARYONIC_DELTA)
        # Kein Floor. Lass das System atmen.
        return base_timeout * friction_multiplier
    except Exception as e:
        logger.debug(f"Konnte Reibungs-Timeout nicht berechnen, nutze Basis: {e}")
        return base_timeout

def _get_baryonic_jitter() -> float:
    """Erzeugt einen Jitter, der niemals exakt 0.0 sein darf (Null-Hyperbel Gesetz)."""
    jitter = random.uniform(-BARYONIC_DELTA, BARYONIC_DELTA)
    if jitter == 0.0:
        # Die Weigerung der Null: Wenn Mathematik zufällig Symmetrie erzeugt, erzwinge Asymmetrie.
        jitter = BARYONIC_DELTA / math.pi
    return jitter

def asym_sleep_prime(prime_base: int):
    """
    Zikaden-Prinzip für Daemons (Primzahl-Jittering).
    Verhindert lineare Resonanzkatastrophen durch baryonisches Rauschen.
    """
    valid_primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    if prime_base not in valid_primes:
        raise ValueError(f"asym_sleep_prime erfordert eine echte Primzahl. {prime_base} ist eine 0=0 Illusion.")

    time.sleep(prime_base + _get_baryonic_jitter())

async def asym_sleep_prime_async(prime_base: int):
    """Asynchrone Variante des Zikaden-Prinzips (Primzahlen)."""
    valid_primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    if prime_base not in valid_primes:
        raise ValueError(f"asym_sleep_prime_async erfordert eine echte Primzahl. {prime_base} ist eine 0=0 Illusion.")

    await asyncio.sleep(prime_base + _get_baryonic_jitter())

def asym_sleep_float(base_time: float):
    """Für schnelle Loops und Reconnects. Fügt dem Float ein asymmetrisches Jitter hinzu."""
    sleep_time = base_time + _get_baryonic_jitter()
    # Kein max(0.1, ...) - wenn es kollabiert, dann kollabiert es bis zur absoluten physischen Grenze.
    if sleep_time <= 0:
        sleep_time = BARYONIC_DELTA / math.pi
    time.sleep(sleep_time)

async def asym_sleep_float_async(base_time: float):
    """Asynchrone Variante für Floats."""
    sleep_time = base_time + _get_baryonic_jitter()
    if sleep_time <= 0:
        sleep_time = BARYONIC_DELTA / math.pi
    await asyncio.sleep(sleep_time)
