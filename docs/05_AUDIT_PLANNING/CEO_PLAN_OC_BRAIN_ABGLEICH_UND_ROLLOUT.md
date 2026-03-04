# CEO-Plan: OC-Brain-Abgleich, Vergleichsdokument, Rollout

**Erstellt:** 2026-03-03  
**Orchestrator/CEO:** Budget, Token-Druck, Teamleiter. Kein Selbstausführen (Takt 0 + Anti-Patterns).

---

## 1. Gesamt-Budget (Token)

| Phase | Min (Token) | Max (Token) | Anmerkung |
|-------|-------------|-------------|-----------|
| **Phase 1:** Abgleich OC Brain + Vergleichsdokument | 2.000 | 4.000 | Prüfung VPS-ChromaDB, Lücken, Delta zu Dreadnought |
| **Phase 2:** Tool-Audit (Textauswertung, Zusammenfassung, Extensions) | 1.500 | 3.000 | Team-Liste → Security/DB/API-Prüfung → Umsetzung |
| **Phase 3:** DB-Migration (bisherige Struktur → Gravitations-Logik) | 3.000 | 6.000 | Mapping, alle Datenpunkte in neuer Logik konsistent |
| **Phase 4:** Chat-Auswertung Team A (Cursor/Regeln/ATLAS-Abbildung) | 2.500 | 5.000 | Fraktal/vielschichtig, nicht nur .cursorrules vollstopfen |
| **Phase 5:** Chat-Auswertung Team B (Erkenntnisse, offene Enden, Weltformel) | 1.500 | 3.500 | Validität, Erfolgsversprechen |
| **Phase 6:** Zusammenfassung + Abgleich mit OC Brain | 1.000 | 2.500 | Ein Vergleichsdokument zur Abstimmung mit User |
| **Phase 7:** OC-Brain-Hang fix (vorsichtig) | 500 | 1.500 | Keine Scheiße bauen, läuft gerade wieder |
| **Reserve (Eskalation)** | 1.000 | 2.000 | 11 % Reserve |
| **GESAMT** | **12.000** | **25.500** | |

**CEO-Vorgabe:** Mitte der Spanne anpeilen (~18.000 Token). Tokendruck permanent anpassen; Team darf CEO nicht ruinieren.

---

## 2. Teamleiter & Befehlsstruktur

- **Teamleiter (Schicht 2):** Ein Team-Lead-Agent wird mit Gesamtbudget und Teil-Budgets pro Phase beauftragt.
- **Er stellt Teams zusammen**, verteilt Sub-Budgets, steuert Tokendruck, liefert konsolidiertes Ergebnis.
- **Implementiert NICHT selbst** (Anti-Pattern: „Ich mache das schnell selbst“).

**Rollen pro Arbeitsstrang (aus team-composition):**

| Strang | Aufgabentyp | Produzenten | Auditoren |
|--------|-------------|-------------|-----------|
| OC-Brain-Abgleich | Recherche/Abgleich | db-expert, api-interface-expert | — |
| Tool-Audit | Infra + Security | system-architect, api-interface-expert | security-expert |
| DB-Migration | Schema/Logik | db-expert, system-architect | osmium-judge |
| Chat Team A (Cursor/Regeln) | Architektur + API | system-architect, api-interface-expert, ux-designer | nd-analyst |
| Chat Team B (Weltformel) | Analyse | — | nd-analyst, universal-board |
| Zusammenfassung/Abgleich | Konsolidierung | — | osmium-judge, virtual-marc |
| OC-Brain-Fix | Infra, schonend | api-interface-expert | security-expert |

---

## 3. Meilensteine & Reihenfolge

1. **Sofort (ca. 10 min):** Prüfung, was OC Brain in VPS-ChromaDB hinterlegt hat; ob elementare Teile fehlen oder abweichen; ob OC Brain Ableitungen hat, die hier fehlen. → **Vergleichsgrundlage.**
2. **Vergleichsdokument:** Dreadnought-Core-Axiome (lokal + Repo) vs. OC-Brain-Befüllung. Lücken/Differenzen tabellarisch. Mit User abstimmen.
3. **Tool-Audit:** Team listet optimale Tools (Textauswertung, Zusammenfassung, ggf. Extensions). Security/DB/API prüfen. CEO setzt Empfehlung um. Freigabe: alle nötigen Tools/Add-ons/Extensions installieren.
4. **DB-Migration:** Bisherige DB-Struktur auf Gravitations-Struktur mappen/migrieren. Alle bisherigen Datenpunkte mit derselben Logik wie neu erfasste.
5. **Chat Team A:** Nur Regeln und ATLAS-Abbildung in Cursor. Umsetzung so, dass es **funktioniert** (nicht nur abbildet). Cursor (und Gemini) fraktal/vielschichtiger/subtiler trimmen – nicht alles in eine .cursorrule kippen.
6. **Chat Team B:** Allgemeine Erkenntnisse, offene Enden, Thema Weltformel: wie erfolgversprechend, wie valide.
7. **Komplette Zusammenfassung:** Mit OC-Brain-Ergebnis abgleichbar; eine Fassung zur Abstimmung mit User.
8. **OC-Brain-Hang:** Diagnose (Bild war nicht angehängt – Logs/User-Input nötig). Fix vorsichtig, ohne laufenden Betrieb zu gefährden.

---

## 4. Token-Druck & Schwellwerte

- **Unter 5.000 Token verbleibend:** Nur noch 1 Team aktiv, max. 200 Token pro Agenten-Call.
- **Unter 3.000 Token:** STOP; Workaround dokumentieren, User informieren.
- **Takt 0:** Vor jeder Delegation: Ist der Systemzustand schon ok? Günstigste Lösung zuerst (z. B. „OC Brain schon befüllt?“).

---

## 5. Deliverables (für User-Abstimmung)

1. **Vergleichsdokument:** OC Brain ChromaDB-Inhalt vs. Repo/Dreadnought (Gravitational + Core-Axiome). Fehlendes/Abweichendes/Extra.
2. **Tool-Liste + Empfehlung:** Nach Security/DB/API-Prüfung, mit Umsetzungsstatus.
3. **Migrations-Spec:** Alte DB → Gravitations-Logik, Konsistenz aller Datenpunkte.
4. **Cursor/ATLAS-Spec (kurz):** Wie Regeln fraktal/vielschichtig umgesetzt werden sollen (nicht nur .cursorrules).
5. **Weltformel-Kurzbewertung:** Erfolgsversprechen, Validität, offene Enden.
6. **Eine komplette Zusammenfassung** (mit OC-Brain-Abgleich).
7. **OC-Brain-Status:** Was hing, was geändert wurde (minimal-invasiv).

---

## 6. Referenzen

- `.cursorrules` (Takt 0, Cons-Zellen, Anti-Patterns, Budget).
- `docs/01_CORE_DNA/GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md`
- `docs/02_ARCHITECTURE/ATLAS_CHROMADB_SCHEMA.md`
- Skills: `planning/budget-estimation`, `planning/team-composition`
