"""
Z-VECTOR DAMPER V2 (Ring-0 Hypervisor)
--------------------------------------
Bidirektionaler Z-Vektor mit Kuehlkreislauf.
Verhindert sowohl Endlosschleifen (Eskalation) als auch thermodynamischen Tod (Ratsche).
V1: Monoton steigend -> garantierter Veto nach 12 Calls.
V2: Decay + Cooling + Session-Rotation -> unendliche Laufzeit moeglich.
"""

import math
import os
import time
import functools
from dataclasses import dataclass, field
from typing import Any, Callable

from src.config.mtho_state_vector import BARYONIC_DELTA

PHI = 1.618033988749895

# Fibonacci-basierte Schwellwerte
MAX_ITERATIONS_PER_SESSION = 13
TOKEN_WARNING_THRESHOLD = 89000
TOKEN_KILL_THRESHOLD = 233000
SESSION_TIMEOUT_S = 3600.0
COOLING_HALF_LIFE_S = 300.0


class RuntimeVetoException(Exception):
    """Harter Abbruch wenn Z >= 0.9 oder Iterations-/Token-Limit erreicht."""
    pass


@dataclass
class MonitorSessionState:
    total_tokens: int = 0
    call_count: int = 0
    successful_calls: int = 0
    consecutive_errors: int = 0
    start_time: float = field(default_factory=time.time)
    last_call_time: float = field(default_factory=time.time)
    z_vector_escalation: float = BARYONIC_DELTA


class RuntimeMonitor:
    """Singleton Hypervisor mit bidirektionalem Z-Vektor."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeMonitor, cls).__new__(cls)
            cls._instance._state = MonitorSessionState()
        return cls._instance

    def _cooling_factor(self) -> float:
        """
        Zeitbasierter Decay: Je laenger seit dem letzten Call,
        desto mehr kuehlt das System ab.
        Exponentieller Zerfall mit Halbwertszeit COOLING_HALF_LIFE_S.
        Minimum: BARYONIC_DELTA (nie 0).
        """
        elapsed = time.time() - self._state.last_call_time
        if elapsed <= 0:
            return 1.0
        decay = math.exp(-0.693 * elapsed / COOLING_HALF_LIFE_S)
        return max(BARYONIC_DELTA, decay)

    def _success_relief(self) -> float:
        """
        Erfolgreiche Calls reduzieren den Druck.
        Ratio erfolgreicher Calls daempft den Gesamtwiderstand.
        """
        total = self._state.call_count
        if total == 0:
            return 1.0
        success_ratio = self._state.successful_calls / total
        return 1.0 - (success_ratio * 0.3)

    def _calculate_z_vector(self) -> float:
        """
        Bidirektionaler Z-Vektor:
        Z = BARYONIC_DELTA + (loop_pressure + token_pressure + error_pressure) * cooling * relief
        
        Steigt bei: Hoher Call-Frequenz, Token-Verbrauch, Fehler-Kaskaden.
        Sinkt bei: Zeit ohne Calls (Cooling), erfolgreiche Operationen (Relief).
        Grenzen: [BARYONIC_DELTA, 1.0 - BARYONIC_DELTA] (0 und 1 verboten).
        """
        cooling = self._cooling_factor()
        relief = self._success_relief()

        loop_pressure = (self._state.call_count / MAX_ITERATIONS_PER_SESSION) ** PHI
        token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD
        error_pressure = (self._state.consecutive_errors * 0.15) ** PHI

        session_age = time.time() - self._state.start_time
        timeout_pressure = max(0.0, (session_age / SESSION_TIMEOUT_S - 0.5)) ** 2

        raw_z = BARYONIC_DELTA + (
            loop_pressure + token_pressure + error_pressure + timeout_pressure
        ) * cooling * relief

        self._state.z_vector_escalation = min(
            1.0 - BARYONIC_DELTA,
            max(BARYONIC_DELTA, raw_z)
        )

        os.environ["MTHO_Z_WIDERSTAND"] = str(self._state.z_vector_escalation)
        return self._state.z_vector_escalation

    def request_execution(self, estimated_tokens: int = 0) -> None:
        """Wird VOR jedem LLM-Call aufgerufen. Prueft harte Grenzen."""
        self._state.call_count += 1
        self._state.last_call_time = time.time()
        z = self._calculate_z_vector()

        if z >= 0.9:
            raise RuntimeVetoException(
                f"[Z-VETO] Z-Vector Critical ({z:.3f}). "
                f"Calls: {self._state.call_count}, Errors: {self._state.consecutive_errors}. "
                "System ueberhitzt. Warte oder rotiere Session."
            )

        if self._state.total_tokens + estimated_tokens > TOKEN_KILL_THRESHOLD:
            raise RuntimeVetoException(
                f"[Z-VETO] Token Limit ({self._state.total_tokens}/{TOKEN_KILL_THRESHOLD}). "
                "Rotiere Session mit rotate_session()."
            )

    def register_usage(self, consumed_tokens: float, success: bool = True) -> None:
        """
        Wird NACH dem Call aufgerufen.
        success=True kuehlt, success=False heizt.
        """
        self._state.total_tokens += int(round(consumed_tokens))

        if success:
            self._state.successful_calls += 1
            self._state.consecutive_errors = 0
        else:
            self._state.consecutive_errors += 1

        self._calculate_z_vector()

    def rotate_session(self) -> dict:
        """
        Session-Boundary-Reset: Setzt Zaehler zurueck,
        behaelt aber den Z-Vektor-Trend als Gedaechtnis.
        Gibt Telemetrie der alten Session zurueck.
        """
        telemetry = self.get_telemetry()

        residual_z = self._state.z_vector_escalation * 0.2
        self._state = MonitorSessionState(
            z_vector_escalation=max(BARYONIC_DELTA, residual_z)
        )

        return telemetry

    def get_telemetry(self) -> dict:
        """Gibt den aktuellen Systemzustand als Dict zurueck."""
        return {
            "z_vector": round(self._state.z_vector_escalation, 4),
            "call_count": self._state.call_count,
            "successful_calls": self._state.successful_calls,
            "consecutive_errors": self._state.consecutive_errors,
            "total_tokens": self._state.total_tokens,
            "session_age_s": round(time.time() - self._state.start_time, 1),
            "cooling_factor": round(self._cooling_factor(), 4),
            "max_iterations": MAX_ITERATIONS_PER_SESSION,
            "token_kill_threshold": TOKEN_KILL_THRESHOLD,
        }


def argos_protected(estimated_tokens_per_call: int = 1000) -> Callable:
    """
    Decorator fuer LLM-Calls.
    Trackt Tokens und Z-Vektor bidirektional.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor = RuntimeMonitor()
            monitor.request_execution(estimated_tokens_per_call)

            try:
                result = func(*args, **kwargs)
                if isinstance(result, str):
                    monitor.register_usage(len(result) / 4, success=True)
                else:
                    monitor.register_usage(estimated_tokens_per_call, success=True)
                return result
            except RuntimeVetoException:
                raise
            except Exception as e:
                monitor.register_usage(estimated_tokens_per_call, success=False)
                raise e
        return wrapper
    return decorator


# Globale Instanz
z_damper = RuntimeMonitor()
argos = z_damper

# Backward-Kompatibilitaet
ArgosVetoException = RuntimeVetoException
MAX_ITERATIONS = MAX_ITERATIONS_PER_SESSION
