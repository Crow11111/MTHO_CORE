"""
Z-VECTOR DAMPER V3 (Ring-0 Hypervisor)
--------------------------------------
Bidirektionaler Z-Vektor mit Kuehlkreislauf und Sliding Window.
V1: Monoton steigend -> Tod nach 12 Calls.
V2: Decay + Cooling + Session-Rotation -> unendliche Laufzeit.
V3: Sliding Window (nur aktueller Druck zaehlt) + API-Token-Praezision.
"""

import logging
import math
import os
import time
import functools
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

from src.config.core_state import BARYONIC_DELTA, SYMMETRY_BREAK
from src.logic_core.crystal_grid_engine import CrystalGridEngine

PHI = 1.618033988749895

MAX_ITERATIONS_PER_SESSION = 13
TOKEN_WARNING_THRESHOLD = 89000
TOKEN_KILL_THRESHOLD = 233000
SESSION_TIMEOUT_S = 3600.0
COOLING_HALF_LIFE_S = 300.0
SLIDING_WINDOW_S = 300.0


class RuntimeVetoException(Exception):
    """Harter Abbruch wenn Z >= 0.9 oder Token-Limit erreicht."""
    pass


@dataclass
class CallRecord:
    """Ein einzelner Call im Sliding Window."""
    timestamp: float
    tokens: int
    success: bool


@dataclass
class MonitorSessionState:
    total_tokens: int = 0
    call_count: int = 0
    successful_calls: int = 0
    consecutive_errors: int = 0
    start_time: float = field(default_factory=time.time)
    last_call_time: float = field(default_factory=time.time)
    z_vector_escalation: float = BARYONIC_DELTA
    call_window: deque = field(default_factory=lambda: deque(maxlen=500))


class RuntimeMonitor:
    """Singleton Hypervisor mit bidirektionalem Z-Vektor und Sliding Window."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RuntimeMonitor, cls).__new__(cls)
            cls._instance._state = MonitorSessionState()
        return cls._instance

    def _prune_window(self) -> None:
        """Entfernt abgelaufene Eintraege aus dem Sliding Window."""
        cutoff = time.time() - SLIDING_WINDOW_S
        while self._state.call_window and self._state.call_window[0].timestamp < cutoff:
            self._state.call_window.popleft()

    def _window_pressure(self) -> tuple:
        """
        Berechnet Druck nur aus dem aktuellen Zeitfenster.
        Gibt (call_rate, token_rate, error_rate) zurueck.
        """
        self._prune_window()
        window = self._state.call_window

        if not window:
            return (0.0, 0.0, 0.0)

        window_calls = len(window)
        window_tokens = sum(r.tokens for r in window)
        window_errors = sum(1 for r in window if not r.success)

        call_rate = window_calls / MAX_ITERATIONS_PER_SESSION
        token_rate = window_tokens / TOKEN_KILL_THRESHOLD
        error_rate = window_errors / max(1, window_calls)

        return (call_rate, token_rate, error_rate)

    def _cooling_factor(self) -> float:
        """Exponentieller Zerfall seit letztem Call. Minimum: BARYONIC_DELTA."""
        elapsed = time.time() - self._state.last_call_time
        if elapsed <= 0:
            return 1.0
        decay = math.exp(-0.693 * elapsed / COOLING_HALF_LIFE_S)
        return max(BARYONIC_DELTA, decay)

    def _success_relief(self) -> float:
        """Erfolgreiche Calls reduzieren den Druck um bis zu 30%."""
        total = self._state.call_count
        if total == 0:
            return 1.0
        success_ratio = self._state.successful_calls / total
        return 1.0 - (success_ratio * 0.3)

    def _calculate_z_vector(self) -> float:
        """
        Z = BARYONIC_DELTA + (window_pressure + error_cascade) * cooling * relief

        Window-basiert: Nur die letzten 5 Minuten zaehlen.
        Lifetime-Zaehler dienen nur der Telemetrie, nicht dem Z-Vektor.
        """
        cooling = self._cooling_factor()
        relief = self._success_relief()

        call_rate, token_rate, error_rate = self._window_pressure()

        loop_pressure = call_rate ** PHI
        token_pressure = token_rate
        error_pressure = (self._state.consecutive_errors * 0.15) ** PHI

        session_age = time.time() - self._state.start_time
        timeout_pressure = max(0.0, (session_age / SESSION_TIMEOUT_S - SYMMETRY_BREAK)) ** 2

        raw_z = BARYONIC_DELTA + (
            loop_pressure + token_pressure + error_pressure + timeout_pressure
        ) * cooling * relief

        # Kristall-Gitter Snapping via CrystalGridEngine
        snapped_z = CrystalGridEngine.apply_operator_query(raw_z)
        self._state.z_vector_escalation = snapped_z

        os.environ["CORE_Z_WIDERSTAND"] = str(self._state.z_vector_escalation)
        return self._state.z_vector_escalation

    def request_execution(self, estimated_tokens: int = 0) -> None:
        """Wird VOR jedem LLM-Call aufgerufen. Prueft harte Grenzen."""
        self._state.call_count += 1
        self._state.last_call_time = time.time()
        z = self._calculate_z_vector()

        if z >= 0.9:
            raise RuntimeVetoException(
                f"[Z-VETO] Z={z:.3f} kritisch. "
                f"Window: {len(self._state.call_window)} Calls, "
                f"Errors: {self._state.consecutive_errors}. "
                "Warte oder rotiere Session."
            )

        if self._state.total_tokens + estimated_tokens > TOKEN_KILL_THRESHOLD:
            raise RuntimeVetoException(
                f"[Z-VETO] Token Limit ({self._state.total_tokens}/{TOKEN_KILL_THRESHOLD}). "
                "Rotiere Session."
            )

    def register_usage(
        self,
        consumed_tokens: float,
        success: bool = True,
        api_usage: Optional[dict] = None,
    ) -> None:
        """
        Wird NACH dem Call aufgerufen.
        api_usage: Dict mit exakten API-Stats (prompt_tokens, completion_tokens).
        Wenn vorhanden, ueberschreibt es die Schaetzung.
        """
        if api_usage:
            exact = api_usage.get("prompt_tokens", 0) + api_usage.get("completion_tokens", 0)
            if exact > 0:
                consumed_tokens = float(exact)

        tokens_int = int(round(consumed_tokens))
        self._state.total_tokens += tokens_int

        self._state.call_window.append(CallRecord(
            timestamp=time.time(),
            tokens=tokens_int,
            success=success,
        ))

        if success:
            self._state.successful_calls += 1
            self._state.consecutive_errors = 0
        else:
            self._state.consecutive_errors += 1

        if self._state.total_tokens >= TOKEN_WARNING_THRESHOLD:
            logger.warning(
                f"[Z-VECTOR DAMPER] Token-Warnung: {self._state.total_tokens}/{TOKEN_WARNING_THRESHOLD} "
                f"({self._state.total_tokens / TOKEN_WARNING_THRESHOLD * 100:.1f}%)"
            )

        self._calculate_z_vector()

    def rotate_session(self) -> dict:
        """Session-Reset mit 20% Residual-Gedaechtnis."""
        telemetry = self.get_telemetry()

        residual_z = self._state.z_vector_escalation * 0.2
        self._state = MonitorSessionState(
            z_vector_escalation=max(BARYONIC_DELTA, residual_z)
        )

        return telemetry

    def get_telemetry(self) -> dict:
        """Systemzustand inkl. Window-Metriken."""
        self._prune_window()
        call_rate, token_rate, error_rate = self._window_pressure()
        return {
            "z_vector": round(self._state.z_vector_escalation, 4),
            "call_count": self._state.call_count,
            "successful_calls": self._state.successful_calls,
            "consecutive_errors": self._state.consecutive_errors,
            "total_tokens": self._state.total_tokens,
            "window_calls": len(self._state.call_window),
            "window_call_rate": round(call_rate, 4),
            "window_token_rate": round(token_rate, 4),
            "window_error_rate": round(error_rate, 4),
            "session_age_s": round(time.time() - self._state.start_time, 1),
            "cooling_factor": round(self._cooling_factor(), 4),
            "max_iterations": MAX_ITERATIONS_PER_SESSION,
            "token_kill_threshold": TOKEN_KILL_THRESHOLD,
        }


def shell_protected(estimated_tokens_per_call: int = 1000) -> Callable:
    """
    Decorator fuer LLM-Calls.
    Trackt Tokens via Sliding Window und Z-Vektor bidirektional.
    Wenn der dekorierte Call ein Dict mit 'usage' Key zurueckgibt,
    werden die exakten API-Stats verwendet.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor = RuntimeMonitor()
            monitor.request_execution(estimated_tokens_per_call)

            try:
                result = func(*args, **kwargs)

                api_usage = None
                if isinstance(result, dict) and "usage" in result:
                    api_usage = result["usage"]

                if api_usage:
                    monitor.register_usage(0, success=True, api_usage=api_usage)
                elif isinstance(result, str):
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
shell = z_damper

# Backward-Kompatibilitaet
ShellVetoException = RuntimeVetoException
MAX_ITERATIONS = MAX_ITERATIONS_PER_SESSION
