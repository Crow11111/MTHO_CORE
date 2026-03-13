# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Ephemeral Agents - Kurzlebige Sub-Instanzen fuer Signal-Vektor 2 (INTENT).
"""
from .core_agent import EphemeralAgent, EphemeralAgentPool

# Backward-Kompatibilitaet
from .core_agent import NightAgentAgent, NightAgentAgentPool  # noqa: F401

__all__ = ["EphemeralAgent", "EphemeralAgentPool", "NightAgentAgent", "NightAgentAgentPool"]
