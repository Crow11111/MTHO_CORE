# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import logging
import time
from typing import Any, Callable

from src.config.core_state import BARYONIC_DELTA

logger = logging.getLogger("core.circuit_breaker")


class CircuitBreakerOpenException(Exception):
    """Raised when a call is attempted while the circuit is open."""


class CircuitBreaker:
    """
    Zustandsbasierter Circuit Breaker (closed -> open -> half_open -> closed).
    Oeffnet nach failure_threshold konsekutiven Fehlern.
    Schliesst nach erstem Erfolg im half_open-Zustand.

    Nutzung:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        result = cb.call(some_sync_function, arg1, arg2)
        result = await cb.call_async(some_async_function, arg1, arg2)
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._state = "closed"

    @property
    def is_open(self) -> bool:
        if self._state == "open":
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = "half_open"
                return False
            return True
        return False

    def _pre_call(self) -> None:
        """Gemeinsame Gate-Logik vor jedem Aufruf."""
        if self._state == "open":
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = "half_open"
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit OPEN ({self._failure_count} Fehler). "
                    f"Recovery in {self.recovery_timeout - (time.time() - self._last_failure_time):.1f}s"
                )

    def _on_success(self) -> None:
        if self._state == "half_open":
            logger.info("CircuitBreaker: half_open -> closed (Erfolg)")
        self._failure_count = 0
        self._state = "closed"

    def _on_failure(self, exc: Exception) -> None:
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(
                "CircuitBreaker: -> OPEN nach %d Fehlern (%s)",
                self._failure_count,
                type(exc).__name__,
            )

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Synchroner Aufruf mit Circuit-Breaker-Schutz."""
        self._pre_call()
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure(exc)
            raise

    async def call_async(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Asynchroner Aufruf mit Circuit-Breaker-Schutz."""
        self._pre_call()
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure(exc)
            raise

    def record_success(self) -> None:
        """Manueller Erfolg (Rueckwaertskompatibilitaet)."""
        self._on_success()

    def record_failure(self) -> None:
        """Manueller Fehler (Rueckwaertskompatibilitaet)."""
        self._on_failure(RuntimeError("manual record_failure"))

    def get_status(self) -> dict:
        return {
            "state": self._state,
            "failures": self._failure_count,
            "threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "delta": BARYONIC_DELTA,
        }
