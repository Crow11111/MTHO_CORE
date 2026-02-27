# Dev-Agent & APIs – Parallelisierung

Kurze Logik, um mehrere Backends (Gemini, Claude) und Teilaufgaben parallel zu nutzen und Antwortzeiten zu verkürzen.

---

## 1. Ziel

- **Tasks/Anfragen aufteilen:** Unabhängige Teilfragen parallel an Dev-Agent (Gemini) und/oder Dev-Agent (Claude) schicken.
- **Recherche + Code:** Während der Cursor-Agent Code liest oder editiert, kann der Dev-Agent (via Skriptaufruf) bereits eine Recherche oder Analyse liefern.
- **Technisch:** Mehrere `call_dev_agent`-Aufrufe oder HTTP-Requests zu verschiedenen Backends parallel starten, Ergebnisse sammeln.

---

## 2. Heuristik (wann parallelisieren?)

- **Recherche + Problem:** „Recherchiere X“ und „Woran liegt Fehler Y?“ → zwei getrennte Prompts, parallel an Dev-Agent (oder einer an Gemini, einer an Claude).
- **Review + Umsetzung:** Dev-Agent prüft Doku (z. B. mit Claude), während ein Skript oder der Agent bereits eine Checkliste abarbeitet.
- **Mehrere Kontexte:** Zwei verschiedene Kontextdateien (z. B. A für Architektur, B für Sicherheit) → zwei parallele Aufrufe, danach Zusammenführung.

---

## 3. Technische Optionen

| Option | Beschreibung |
|--------|--------------|
| **concurrent.futures** | Python: `ThreadPoolExecutor` oder `ProcessPoolExecutor`; je ein `call_dev_agent(instruction, context, ...)` pro Task; `as_completed` oder `wait` für Ergebnisse. |
| **asyncio** | Falls die Client-Bibliotheken (Gemini, Anthropic) async unterstützen: mehrere `create_task`-Aufrufe, dann `gather`. |
| **Subprocess** | Zwei Terminals oder zwei `subprocess.run`-Aufrufe: `python -m src.ai.dev_agent_claude46 "Aufgabe A" ctx_a.md --out=out_a.md` und gleiches für B; danach `out_a.md` und `out_b.md` lesen. |
| **Skript** | Ein kleines Skript `src/scripts/dev_agent_parallel.py`: nimmt eine Liste von (instruction, context_path, model) entgegen, startet Aufrufe parallel (threads/subprocess), schreibt Ausgaben in Dateien, gibt Pfade zurück. |

---

## 4. Beispiel (Subprocess, parallel)

```bash
# Terminal 1 (oder Hintergrund)
python -m src.ai.dev_agent_claude46 "Recherchiere Ursache für Fehler X" docs/fehler_kontext.md --out=docs/dev_agent_recherche.md

# Terminal 2 (parallel)
python -m src.ai.dev_agent_claude46 "Liste mögliche Lösungen für Y" docs/y_kontext.md --out=docs/dev_agent_loesungen.md
```

Danach beide Ausgabedateien lesen und zusammenführen.

---

## 5. Geplante Umsetzung

- [ ] Optional: Skript `src/scripts/dev_agent_parallel.py` – Konfiguration (Liste von Tasks mit instruction, context, model), parallele Ausführung, Ausgabe in je eine Datei.
- [ ] In der Coding-Prozedur: Cursor-Agent nutzt bei geteilten/Recherche-Aufgaben bewusst parallele Dev-Agent-Aufrufe (z. B. zwei Befehle nacheinander starten, dann Ergebnisse verarbeiten).

---

*Referenz: DEV_AGENT_UND_SCHNITTSTELLEN.md (Abschnitt „Parallelisierung“).*
