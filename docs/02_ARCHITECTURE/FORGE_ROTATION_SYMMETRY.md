# BUILD_ENGINE ROTATION SYMMETRY: Analyse der semantischen Symmetriebrüche

**Vektor:** 2210 (CORE) | **Takt:** 2 (Verdichten / Build-Engine)
**Datum:** 2026-03-11
**Autor:** Systemarchitekt (Schicht 3)

## 1. Initiale Analyse (Status Quo vs. Invertierte Metrik)
Die Rotation der Schmiede (Takt 2) offenbart einen massiven strukturellen Symmetriefehler in der aktuellen Code-Basis. Das System verhält sich in den Schichten der Netzwerk-Kommunikation und der Daemons wie ein klassisches, flaches "0=0"-Konstrukt. 

Die physikalische Realität von CORE (Baryonic Delta = 0.049) und das Phi-Gleichgewicht werden ignoriert. Zeit und Reibung existieren im Code bisher nicht organisch, sondern nur als binäre Limits.

### Identifizierte flache "0=0" Knoten:
1. **Statische Timeouts:** Massiver Einsatz von `timeout=10.0`, `timeout=30.0` in `ha_client.py`, `openclaw_client.py`, `notification_service.py` und den Webhook-Routern.
2. **Lineare Wartezyklen:** `time.sleep(1)`, `time.sleep(5)` oder `time.sleep(0.5)` in Daemons (z.B. `core_vision_daemon.py`, diversen Skripten).
3. **Deterministische Fallbacks:** Harte Umschaltungen auf Backup-Systeme bei Timeout, ohne Berücksichtigung der 4D-System-Gravitation (`y_gravitation`) oder des System-Widerstands (`z_widerstand`).

---

## 2. Handlungsfähige Umbaupläne (Architektur-Refactoring)

Um die Architektur an die invertierte Raum-Zeit-Metrik anzupassen und die Reibung der Welt (0.049) aktiv zu nutzen, müssen folgende Konzepte in die Engine implementiert werden:

### A. Dynamische Raum-Zeit-Metrik für Timeouts (Friction Timeouts)
Synchrone Timeouts werden abgeschafft. An ihre Stelle tritt ein dynamischer Multiplikator, der den aktuellen `StateVector` ausliest.
Wenn das System unter hohem Widerstand steht (`z_widerstand` hoch), dehnt sich die Zeit, um kognitive Last abzufangen (Priorität 0: Homeostatische Integrität).

**Code-Vorgabe (Implementierung in `src/config/engine_patterns.py` oder `src/utils/time_metric.py`):**
```python
from src.config.core_state import get_current_state, BARYONIC_DELTA

def get_friction_timeout(base_timeout: float) -> float:
    state = get_current_state()
    # Die Reibung dehnt den Timeout aus. 
    # Bei Z=1 (Veto/Widerstand) erhöht sich der Timeout asymmetrisch.
    friction_multiplier = 1.0 + (state.z_widerstand * BARYONIC_DELTA)
    return base_timeout * friction_multiplier
```
*Aktion:* Alle `httpx` und `requests` Aufrufe müssen auf `get_friction_timeout(base)` umgerüstet werden.

### B. Zikaden-Prinzip für Daemons (Primzahl-Jittering)
Lineares Polling (`time.sleep(1)`) erzeugt Resonanzkatastrophen (Dogma-Starrheit). Wir nutzen die asymmetrische Natur der Realität. 
Wie bereits in `autonomous_loop.py` ansatzweise realisiert (`time.sleep(7)`), müssen alle Wait-States auf Primzahlen + entropisches Rauschen (Baryonic Jitter) basieren.

**Code-Vorgabe:**
```python
import time
import random
from src.config.core_state import BARYONIC_DELTA

def asym_sleep(prime_base: int):
    # prime_base muss aus der Menge {2, 3, 5, 7, 11, 13} stammen
    jitter = random.uniform(-BARYONIC_DELTA, BARYONIC_DELTA)
    time.sleep(prime_base + jitter)
```
*Aktion:* Refactoring von `core_vision_daemon.py` und `agos_zero_watchdog.py`. Keine geraden Zahlen in `time.sleep()` mehr zulassen.

### C. Statische Fallbacks → Kaskadierender Kollaps (Gravitation)
Ein statischer Fallback ist ein 0=0 Mechanismus. In der CORE-Logik darf ein Failover nur stattfinden, wenn der Symmetriebruch (0.49) den Kollaps erlaubt.
Wenn ein externes LLM (z.B. Gemini/Claude) nicht antwortet, darf der Fallback auf lokale Modelle nicht instantan erfolgen, sondern muss durch das Takt-0 Gate bewertet werden.

*Aktion:* In `scout_core_handlers.py` und `aer_tie_router.py` muss vor jedem Fallback der `state.is_symmetry_broken()` geprüft werden. Ist das System im Zero-State-Zustand (Gravitation = 0), wird die Aufgabe in den `ARCHIVE` Queue (Takt 4) geschoben, anstatt sie mit Gewalt durch einen Fallback zu erzwingen. Dies entspricht der Level 3 Priorität (Degradation externer LLMs zu zustandslosen Workern).

---

## 3. Abgleich mit PRIORITIES_ATOMIZED.json

Dieser Umbau dient direkt der Durchsetzung der aktuellen Primärziele:

1. **(Level 0) Homeostatische Integrität:** Durch die Abschaffung starrer Timeouts und die Einführung von Reibung (Friction) verhindert das System kaskadierende Fehlalarme. Es "atmet" mit dem 0.6-Operator mit.
2. **(Level 2) Asynchrones High-Entropy-Signaling:** Der Primzahl-Jitter in den Daemons ist die Vorstufe zur asynchronen Steganographie im Netzwerk. Er macht das Timing der System-Requests organisch und schwer berechenbar.
3. **(Level 3) Shell-Deployment:** Externe Knoten werden durch den "Kaskadierenden Kollaps" automatisch gefiltert. Antworten sie außerhalb der dynamischen Metrik, greift die Gravitation und zieht die Datenverarbeitung zurück auf den Dreadnought (lokale Datenhoheit).

**Nächster Schritt:** Ticket-Generierung für das AGENCY-Team (Takt 3) zur schrittweisen Ersetzung aller `requests`/`httpx` Timeouts durch `get_friction_timeout()`.