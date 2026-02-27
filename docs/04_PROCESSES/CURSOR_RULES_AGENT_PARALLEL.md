# Regeln für Agent-Parallelisierung (zum Übernehmen in allgemeine Cursor Rules)

Diese Regeln sind in **.cursorrules** (Workspace) und **.cursor/rules/task-parallelization-dev-agent.mdc** (Workspace) hinterlegt. Für die **allgemeinen Cursor Rules** (Einstellungen → Rules for AI / User-global) kannst du den folgenden Text übernehmen oder referenzieren.

---

## Selbst ausführen
- Alles, was der Cursor-Agent selbst tun kann, tut er selbst. Nicht den User fragen oder sagen, er solle etwas machen – ausführen. Keine Angewohnheit, Aufgaben an Marc zu delegieren.
- **Scripte:** Im Zuge eines Auftrags Scripte (z. B. `python -m src.scripts.*`) nicht vorschlagen oder „du kannst … ausführen“ sagen – sie selbst ausführen. Kein „führe das Skript aus“ an den User delegieren.

## Dev-Agent
- **Priorisierung:** Initial immer prüfen – für Qualität, Umsetzungsgeschwindigkeit der Einzelaufgabe, Umsetzungsgeschwindigkeit des Gesamtprojekts (Parallelisierung), Kosten/Ressourcen: Ist es besser, den Dev-Agent einzubinden? Dementsprechend priorisieren.
- **Timeout:** Reagiert der Dev-Agent nicht innerhalb angemessener Zeit: ohne ihn weiterlaufen, nicht blockieren.

## Beschäftigte Agents
- Ist Cursor-Agent oder Dev-Agent bereits mit einem Task beauftragt und noch beschäftigt: einbeziehen. Entweder in Warteschlange beim Dev-Agent platzieren, oder selbst durchführen, oder einen weiteren Cursor-Agenten für die Teilaufgabe einsetzen.
- Rollenbeschreibungen (.agents/skills/) nutzen: Im Zweifel einzelne Agents losschicken, Teilaufgaben/Teilbereiche zuweisen.

## Teilergebnisse und Tests
- Sobald etwas teilfertig und für sich testbar/abschließbar ist: Testrolle (bzw. Test-Agent/Skill) damit beauftragen. Nicht warten, bis alles fertig ist.
- Nicht alles selbst prüfen und dann alles teil für teil selbst abarbeiten – Parallelisierung nutzen, Tasks parallel erledigen.
