# Takt 0 (Diagnose) – Vor Delegation und vor jeder kritischen Aktion

**Zweck:** Kein Token verbrennen für unnötige Problemlösung. Kein Umbau kritischer Teile, nur weil ein erster Versuch fehlschlug oder der Kontext weggebrochen ist.

---

## 1. Grundregel

**Bevor** delegiert wird oder in aufwändige Fehleranalyse/Umbaumaßnahmen gegangen wird:

1. **Systemzustand prüfen:** War es ein einmaliger Aussetzer? (z. B. Netz, Dienst nicht bereit, Timeout)
2. **Kurz warten und erneut versuchen:** 1–2 Sekunden Wartezeit + erneuter Test kosten weniger als 200 Sekunden unnötige Problemlösung oder – schlimmer – ein Agent, der kritische Teile umbaut, weil er den etablierten Weg nicht kennt.
3. **Nachschlagen:** Gibt es einen etablierten Weg? Siehe `docs/04_PROCESSES/STANDARD_AKTIONEN_UND_NACHSCHLAG.md`. Nicht neu erfinden, nicht SSH/VPS/Prozedur "fixen", wenn die Doku den Weg beschreibt.

---

## 2. Verboten vor Takt 0

- **Sofort loslaufen** mit Umbau, Refactoring oder "Fix" von Infrastruktur (SSH, Tunnel, Auth, Chroma, HA), ohne:
  - mindestens einen erneuten Versuch (Retry) mit kurzer Verzögerung;
  - Prüfung, ob etwas nur "hing" (Dienst neu starten, Port wieder da);
  - Nachschlagen in Standard-Aktionen / Doku.
- **Kritische Module umbauen** ohne Freigabe durch den Code-Sicherheitsrat (siehe `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md`). Dazu zählen: SSH/Tunnel-Logik, Auth, Chroma-Client, HA-Connector, VPS-Skripte, .env-Handling, Core-API-Routen.

---

## 3. Ablauf (kurz)

1. Aufgabe/Fehler erkannt.
2. **Takt 0:** Zustand prüfen (evtl. 1–2 s warten, erneut testen). In Standard-Aktionen nachschlagen.
3. Wenn etablierter Weg existiert: diesen ausführen (oder erneut ausführen), nicht umbauen.
4. Wenn Änderung an geschütztem Modul nötig: Freigabe einholen (Security Council), nicht ohne Freigabe ändern.
5. Erst danach: Delegation oder tiefere Fehleranalyse.

---

**Referenz:** `.cursorrules` (Takt 0), `STANDARD_AKTIONEN_UND_NACHSCHLAG.md`, `CODE_SICHERHEITSRAT.md`.
