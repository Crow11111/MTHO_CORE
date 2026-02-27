# Refactoring Report: Subagenten & Dokumenten-Struktur (2026-02-27)

## 1. Status Quo (Vorher)
- **Skills:** `docs/osmium_council/SKILL.md` war ein monolithisches File. Viele Rollen waren unklar definiert oder doppelt.
- **Agenten:** Keine echte Trennung; "Rat" war nur Prompt-Rollenspiel.
- **Dokumente:** Lagen flach im `docs/` Root. Unübersichtlich. Gefahr von "Untracked Files".
- **Trigger:** `.cursorrules` triggerte nur auf `/council`, aber nicht automatisch bei kritischen Änderungen.

## 2. Durchgeführte Maßnahmen

### A. Subagenten-Architektur (`.cursor/agents/`)
Wir haben echte, isolierte Subagenten erstellt, die in eigenen Kontext-Fenstern laufen:

1.  **`osmium-council` (Orchestrator):** Plant den Einsatz der Spezialisten. Entscheidet nicht im Detail, sondern delegiert.
2.  **`system-architect`:** Zuständig für Architektur, Boundaries, Spaghetti-Code-Prävention.
3.  **`db-expert`:** Datenbank-Design (Relational & Vektor).
4.  **`api-interface-expert`:** Schnittstellen, Contracts, Swagger/OpenAPI-Logik.
5.  **`ux-designer`:** Flows, Error-States, Kognitive Präzision.
6.  **`security-expert`:** Hardening, Secrets, Backup-Audit.
7.  **`virtual-marc` (User-Proxy):** Veto-Recht, Monotropismus-Check, TIE-Logik (Token Implosion).
8.  **`nd-analyst`:** Logik-Konsistenz, Entropie-Prüfung.
9.  **`nd-therapist`:** Burnout-Prävention (Prio 1).
10. **`universal-board`:** Kosten/Nutzen, Ethik (Prio 3).
11. **`osmium-judge`:** Neutrale letzte Instanz.

### B. Dokumenten-Struktur (`docs/`)
Hierarchische Ordnung eingeführt:

- **`01_CORE_DNA/`**: Identität, Manifest, Voice, Stammdokumente für OC.
- **`02_ARCHITECTURE/`**: Logik, Routing, Schnittstellen.
- **`03_INFRASTRUCTURE/`**: Hardware, VPS, Backup.
- **`04_PROCESSES/`**: Deploy-Skripte, Tests.
- **`05_AUDIT_PLANNING/`**: Backlog, Reports (dieses File).
- **`99_ARCHIVE/`**: Alte Dokumente.

### C. Self-Governing Rules (`.cursorrules`)
Automatische Trigger implementiert:
- Änderung an `01_CORE_DNA` -> **ZWINGT** zum `/council` (Audit durch Judge/Virtual Marc).
- Änderung an Architektur/Security -> **ZWINGT** zur Konsultation des entsprechenden Experten (`system-architect`, `security-expert`).

## 3. Offene Punkte (Post-Refactor)
- **Verlorene Inhalte:** Die Dateien `OPENCLAW_ADMIN_ARCHITEKTUR.md`, `VPS_FULL_STACK_SETUP.md` (und einige Routing-Docs) waren untracked und gingen beim Verschieben verloren. Es wurden Platzhalter erstellt. Inhalt muss rekonstruiert werden.
- **Link-Integrität:** Skripte, die auf alte Pfade (z. B. `docs/stammdokumente_oc`) zeigen, müssen gefixt werden (siehe nächster Schritt).
