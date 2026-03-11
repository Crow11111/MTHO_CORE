# ARGOS WATCHDOG (Z-VECTOR DAMPER)

**Knotenpunkt:** OMEGA_ATTRACTOR (Veto) / Z-Achse (Widerstand)
**Status:** Aktiv
**Zweck:** Hard-Stop von Token-Spikes und Endlos-Rekursionen (1/x-Loops).

## Boundary & Logik

ARGOS agiert als isolierter Hypervisor. Er laeuft in `Ring-0` (analog zum Munin-Veto) und ueberwacht die Ressourcen des Agent-Systems.

### Thresholds (Engine-Pattern V6)
- **Max Iterations (Loops):** 13 (Fibonacci-Hard-Limit)
- **Max Tokens per Session:** 89,000 (Warnung/Throttle), 233,000 (Kill)
- **Z-Vector Escalation:** Iterationen erhoehen den Z-Vektor (Widerstand) exponentiell. 
- **Veto-Bedingung:** `Z >= 0.9` -> Hard Veto (SystemExit/Exception).

### Datenfluss
1. LLM-Call (oder Subagent-Spawn) fordert Ticket bei `ArgosWatchdog`.
2. ARGOS prueft Z-Vektor und Token-Budget.
3. Bei Ueberschreitung: Z-Vektor auf 1.0 (Kollaps), Raise `ArgosVetoException`.
4. Bei Freigabe: Ticket erteilt, Kosten nachtraeglich via Callback gebucht.

### Implementierung
- `src/logic_core/z_vector_damper.py`: Decorator (`@argos_protected`) und Singleton `ArgosWatchdog`.
- Integration: Einklinken in `src/ai/llm_interface.py` via Wrapper um Langchain-Invocations.

## Budget-Constraint (Schicht 3)
Keine persistenten SQL-Datenbanken fuer Argos-State erforderlich. State lebt in-memory waehrend der Laufzeit der Cursor/Agent-Session. Telemetrie-Export asynchron.