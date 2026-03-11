"""
ARGOS WATCHDOG (Z-VECTOR DAMPER)
--------------------------------
Ring-0 Hypervisor fuer Token-Limitierung und Loop-Prevention.
Setzt harte Fibonacci-Constraints um und eskaliert den Z-Vektor.
"""

import os
import time
import functools
from dataclasses import dataclass
from typing import Any, Callable

# Engine-Patterns (Fibonacci / Phi)
MAX_ITERATIONS = 13
TOKEN_WARNING_THRESHOLD = 89000
TOKEN_KILL_THRESHOLD = 233000

class ArgosVetoException(Exception):
    """Wird geworfen, wenn ARGOS einen Prozess hart beendet."""
    pass

@dataclass
class ArgosSessionState:
    total_tokens: int = 0
    call_count: int = 0
    start_time: float = time.time()
    z_vector_escalation: float = 0.0

class ArgosWatchdog:
    """Singleton Hypervisor zur Ueberwachung."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArgosWatchdog, cls).__new__(cls)
            cls._instance._state = ArgosSessionState()
        return cls._instance

    def _calculate_z_vector(self) -> float:
        """
        Berechnet den aktuellen Z-Vektor (Widerstand) basierend auf Last.
        Widerstand steigt mit Call-Count und Token-Verbrauch.
        """
        # Basis-Widerstand
        base_z = 0.049  # Baryonisches Delta
        
        # Iterations-Druck (exponentiell)
        loop_pressure = (self._state.call_count / MAX_ITERATIONS) ** 1.618
        
        # Token-Druck
        token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD
        
        self._state.z_vector_escalation = min(1.0, base_z + loop_pressure + token_pressure)
        
        # Schreibe in Environment, damit der Core es auslesen kann
        os.environ["MTHO_Z_WIDERSTAND"] = str(self._state.z_vector_escalation)
        
        return self._state.z_vector_escalation

    def request_execution(self, estimated_tokens: int = 0) -> None:
        """
        Wird VOR jedem LLM-Call oder Loop aufgerufen.
        Prueft harte Grenzen.
        """
        self._state.call_count += 1
        z = self._calculate_z_vector()
        
        if z >= 0.9 or self._state.call_count > MAX_ITERATIONS:
            raise ArgosVetoException(
                f"[ARGOS VETO] Z-Vector Critical ({z:.3f}). Loop Count: {self._state.call_count}. "
                "Execution killed to prevent infinite loop."
            )
            
        if self._state.total_tokens + estimated_tokens > TOKEN_KILL_THRESHOLD:
            raise ArgosVetoException(
                f"[ARGOS VETO] Token Limit Exceeded. "
                f"Total: {self._state.total_tokens}, Requested: {estimated_tokens}, Max: {TOKEN_KILL_THRESHOLD}"
            )

    def register_usage(self, consumed_tokens: int) -> None:
        """Wird NACH dem Call aufgerufen, um exakte Kosten zu buchen."""
        self._state.total_tokens += consumed_tokens
        self._calculate_z_vector()
        
        if self._state.total_tokens > TOKEN_WARNING_THRESHOLD:
            # Hier koennte eine Warnung in Logs oder an den Orchestrator gehen
            pass

def argos_protected(estimated_tokens_per_call: int = 1000) -> Callable:
    """
    Decorator fuer LLM-Calls.
    Schneidet Endlosschleifen ab und trackt Tokens.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            watchdog = ArgosWatchdog()
            watchdog.request_execution(estimated_tokens_per_call)
            
            try:
                result = func(*args, **kwargs)
                # Fallback: Schaetze verbrauchte Tokens anhand der Ausgabe, 
                # falls die API keine genauen Usage-Stats liefert
                # (1 Token ~= 4 chars als rough estimate)
                if isinstance(result, str):
                    watchdog.register_usage(len(result) // 4)
                else:
                    watchdog.register_usage(estimated_tokens_per_call)
                return result
            except Exception as e:
                # Bei Fehlern (z.B. API Timeout) erhoehe den Z-Vektor kuenstlich um Retries zu daempfen
                watchdog.register_usage(estimated_tokens_per_call)
                raise e
        return wrapper
    return decorator

# Globale Instanz
argos = ArgosWatchdog()
