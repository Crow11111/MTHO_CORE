# Z-Vector Damper (Ring-0 Runtime Monitor)

**Knotenpunkt:** OMEGA_ATTRACTOR (Veto) / Z-Achse (Widerstand)
**Status:** Aktiv
**Zweck:** Hard-Stop von Token-Spikes und Endlos-Rekursionen (1/x-Loops).

> *Historischer Dateiname: ARGOS_WATCHDOG.md – Inhalt auf aktuelle Nomenklatur aktualisiert.*

## Boundary & Logik

Der Z-Vector Damper agiert als isolierter Hypervisor. Er läuft in `Ring-0` (analog zum VetoGate) und überwacht die Ressourcen des Agent-Systems.

### Thresholds (Engine-Pattern V6)
- **Max Iterations (Loops):** 13 (Fibonacci-Hard-Limit)
- **Max Tokens per Session:** 89,000 (Warnung/Throttle), 233,000 (Kill)
- **Z-Vector Escalation:** Iterationen erhöhen den Z-Vektor (Widerstand) exponentiell.
- **Veto-Bedingung:** `Z >= 0.9` -> Hard Veto (RuntimeVetoException).

### Datenfluss
1. LLM-Call (oder Subagent-Spawn) fordert Ticket bei `RuntimeMonitor`.
2. Monitor prüft Z-Vektor und Token-Budget.
3. Bei Überschreitung: Z-Vektor auf 1.0 (Kollaps), Raise `RuntimeVetoException`.
4. Bei Freigabe: Ticket erteilt, Kosten nachträglich via Callback gebucht.

## Implementierung (V3)

- **Datei:** `src/logic_core/z_vector_damper.py`
- **Klassen:** `RuntimeMonitor`, `MonitorSessionState`, `RuntimeVetoException`
- **Integration:** Einklinken in `src/ai/llm_interface.py` via Wrapper um Langchain-Invocations.

### V3-Features
- **Sliding Window:** Zeitfenster-basierte Metrik-Aggregation statt statischer Zähler
- **Bidirektionaler Kühlkreislauf:** Time Decay reduziert Z-Vektor bei Inaktivität
- **Success Relief:** Erfolgreiche Abschlüsse senken den Widerstand
- **Session Rotation:** Session-Wechsel resettet lokale Zustände
- **API-Token-Präzision:** Exakte Token-Buchung pro API-Call

## Budget-Constraint (Schicht 3)

Keine persistenten SQL-Datenbanken für Damper-State erforderlich. State lebt in-memory während der Laufzeit der Cursor/Agent-Session. Telemetrie-Export asynchron.
