# PLAN V6: CORE COCKPIT (UI / UX / TOOLING)

**Datum:** 10. März 2026
**Fokus:** Frontend-Werkzeuge, funktionale Ansicht "von vorne", kognitive Ergonomie.
**Status:** Neutralisiert & Bereinigt (Metaphern entfernt).

---

## 1. Die Prämisse (Kognitive Ergonomie)

Dieser Plan definiert das primäre User Interface.
**Das Problem:** Fragmentierung (CLI-Fenster, unlesbare Log-Streams, Kontext-Wechsel). Das erzeugt kognitiven Overload.
**Die Lösung:** Ein einheitliches, webbasiertes Cockpit (React/Vite). Ein Raum, der nur das zeigt, was im aktuellen Arbeitszyklus relevant ist. Keine Personalisierung, keine Mythen – reine Funktionalität.

---

## 2. Die 4 essenziellen Werkzeuge (Das Frontend)

Das Layout besteht aus vier funktionalen, nahtlos integrierten Bereichen:

### Werkzeug A: Telemetry HUD (System-Metriken)
*Bereits im Ansatz implementiert.*
- **Optik:** Eine schmale Leiste am oberen Bildschirmrand (Dark Mode, reduzierter Kontrast).
- **Funktion:** Zeigt den Live-Zustand der Core-Engine.
- **Inhalt:**
  - **Latenz:** Ping in ms (Indikator für API-Gesundheit).
  - **Git-Status:** Repositorien synchron? (Verhindert Code-Drift).
  - **Friction Guard:** Ein Counter für Regelverstöße (Constraint Violations) während der LLM-Generierung.

### Werkzeug B: Command Console (Eingabe / Interaktion)
- **Optik:** Ein minimalistisches Command-Interface am unteren oder linken Rand. Fokus auf Typografie und Leerraum.
- **Funktion:** Der primäre Input-Kanal.
- **Features:**
  - **Markdown-Support** für Code-Snippets.
  - **LLM-Kontext-Indikator:** Zeigt an, welches Modell (Fast, Reasoning, Base) aktuell den Request verarbeitet.

### Werkzeug C: Validation Build-Engine (Audit- & Rotations-Ansicht)
*Das wichtigste Tool für komplexe Planungen und Code-Reviews.*
- **Optik:** Ein Split-Screen-Board, das sich nur öffnet, wenn komplexe Tasks (Architektur, Multi-Step) geprüft werden.
- **Funktion:** Visualisiert den automatisierten Review-Prozess (Multi-Agent-Audit).
- **Features:**
  - **Links:** Der aktuelle Entwurf / Code.
  - **Rechts:** Die Constraints und Einwände der Sub-Routinen (Security, Architecture, Performance).
  - **Trigger ("Build-Engine Rotation"):** Ein manueller oder automatischer Button, der den Entwurf durch die nächste Iteration zwingt, bis alle Constraints erfüllt sind (Exit Code 0).

### Werkzeug D: Dependency Graph (Architektur-Map)
- **Optik:** Eine optionale, visuelle Knoten-Map.
- **Funktion:** Zeigt, wie Dokumente, Module und State-Vektoren zusammenhängen.

---

## 3. Design-Philosophie (ND-Optimiert)

Um kognitive Last zu minimieren:
1. **Kein Auto-Scrolling:** Text bleibt statisch, während gelesen wird.
2. **Absolute Ruhe im Idle-State:** Keine "Loading-Spinner", wenn das Netzwerk idle ist.
3. **Binäre Zustände:** Systemfehler sind hart blockierend (rot). Keine subtilen Warnungen.
4. **Farbpalette:**
   - Hintergrund: Deep Space (#121212)
   - Typografie: Neutrales Grau (#E0E0E0)
   - Highlights: Bernsteingold (#FFB300) für Kern-Informationen.
   - Warnungen: Helles Rot (#FF5252).
