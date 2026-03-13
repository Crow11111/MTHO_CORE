<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Post-Iteration Audit: 3-Schichten-Modell & Systemanpassungen

**Datum:** 2026-03-01  
**Kontext:** Iterationssprung – 3-Schichten-Modell, Holschuld, Evolutionsprinzip, Virtual-Marc-Repositionierung, Simulationstheorie-Collection, Rueckwaertsevolution  
**Status:** AUDIT – Priorisierte Aenderungsliste

---

## ANTWORTEN AUF DIE PRUEFFRAGEN

### 1. Ring-0-Direktiven vs. 3-Schichten-Modell: Konsistenz?

**TEILWEISE INKONSISTENT.**

Die Ring-0-Direktiven (BIAS_DEPTH_CHECK, NEGENTROPIE_CHECK, KONSTRUKTIVE_DISSONANZ, SCAFFOLDING) in `bias_damper.py` und `PROMPT_B_TECHNICAL_FRAMING.md` verwenden noch die **alte Ring-Hierarchie** (Ring 0 = Kernel-Safety, Ring 1 = Predictive Auditor). Das 3-Schichten-Modell in `.cursorrules` ersetzt diese Hierarchie durch Orchestrator/Teamleiter/Produzenten.

**Bewertung:** Kein Bruch, aber **Terminologie-Drift**. Die Ring-0-Direktiven operieren auf einer anderen Ebene (kognitive Sicherheit des LLM-Outputs) als das 3-Schichten-Modell (Agentenkoordination). Beide koennen koexistieren, aber die Dokumentation muss klar machen, dass Ring-0 ein **Cross-Cutting-Concern** ist, der INNERHALB jeder Schicht wirkt – nicht eine alternative Hierarchie.

### 2. PROMPT_B_TECHNICAL_FRAMING.md: Aktualisierung noetig?

**JA. DRINGEND.**

Drei kritische Inkonsistenzen:
- **"Level 0 (Pilot/Executive): Marc. Die finale Entscheidungsinstanz."** – WIDERSPRICHT dem neuen Modell, wo Marc NICHT der Entscheider ist. Die Struktur entscheidet. Marc ist der wichtigste Experte (via Virtual Marc), aber Scaffolding schuetzt ihn vor sich selbst.
- **Ring-basierte Topologie** ohne Erwaehnung des 3-Schichten-Modells
- **Kein Holschuld-Prinzip, kein Evolutionsprinzip**
- **OMEGA_ATTRACTOR als "Ring 1 Predictive Auditor"** – veraltet, OCBrain ist Teil der VPS-Infrastruktur, nicht die Koordinationsschicht

### 3. Rueckwaertsevolution in System-Dokumenten?

**FEHLT KOMPLETT.**

Das Konzept der Rueckwaertsevolution als AGI-Genese-Modell (System evolviert rueckwaerts von fertiger Vision zu implementierbaren Schritten) ist nirgends in den System-Dokumenten formalisiert. Es existiert nur als implizite Denkfigur. Muss als Konzept in `docs/01_CORE_DNA/` aufgenommen werden.

### 4. Holschuld-Prinzip in allen Agenten?

**NEIN. Nur in 2 von 13 Dateien.**

Holschuld-Prinzip explizit referenziert in:
- `.cursorrules` (Abschnitt 7)
- `.cursor/agents/team-lead.md` (ausfuehrlich)

**FEHLT** in allen 11 Schicht-3-Agenten:
- `virtual-marc.md` – erwaehnt Eskalationsrecht, aber nicht die Holschuld als Prinzip
- `nd-analyst.md`, `nd-therapist.md`, `system-architect.md`, `db-expert.md`, `security-expert.md`, `api-interface-expert.md`, `osmium-judge.md`, `ux-designer.md`, `universal-board.md` – keine Erwaehnung
- `osmium-council.md` – ausserhalb der Hierarchie, Holschuld trotzdem relevant

### 5. simulation_evidence in RAG-Pipeline?

**NICHT EINGEBUNDEN.**

- `query_simulation_evidence()` existiert in `chroma_client.py` (Zeile 194)
- Wird in **keiner** Route, keinem LLM-Call, keiner Pipeline aufgerufen
- Die 28 Indizien liegen in ChromaDB, sind aber **Dead Data** – kein System-Zugang
- Weder `bias_damper.py` noch `llm_interface.py` noch die API-Routen referenzieren die Collection

### 6. Welche Dateien muessen geaendert werden?

Siehe Prioritaetenliste unten.

---

## PRIORITAETENLISTE

### PRIORITAET 1: KRITISCH (Systeminkonsistenz, muss sofort behoben werden)

| # | Datei | Aenderung | Warum |
|---|-------|-----------|-------|
| 1.1 | `docs/01_CORE_DNA/PROMPT_B_TECHNICAL_FRAMING.md` | Komplett ueberarbeiten: (a) "Level 0 Marc = finale Entscheidungsinstanz" ersetzen durch Scaffolding-Paradigma, (b) 3-Schichten-Modell als Referenz, (c) Ring-0 als Cross-Cutting-Concern deklarieren (nicht als Hierarchie-Ebene), (d) Holschuld + Evolutionsprinzip aufnehmen, (e) DUAL-WRITE-Kommentar am Ende aktualisieren | PROMPT_B ist der System-Prompt fuer OCBrain. Wenn OCBrain Marc als "finale Entscheidungsinstanz" behandelt, untergraebt es das gesamte Scaffolding. Zentraler Widerspruch. |
| 1.2 | `docs/01_CORE_DNA/PROMPT_A_USER_PERSONA.md` | "Level 0 (Pilot/Executive)" in Zeile 9 ersetzen durch: "Marc ist der wichtigste Experte und Domaenenquelle, aber NICHT die finale Entscheidungsinstanz. Das System (Scaffolding) schuetzt den User vor Hyper-Fokus-Schleifen." | Gleicher Widerspruch wie PROMPT_B. Marc als "Level 0 Executive" ist das alte Modell. |
| 1.3 | `docs/01_CORE_DNA/CREW_MANIFEST.md` | Komplett ueberarbeiten oder als DEPRECATED markieren. Verwendet alte Rollennamen (ARCHITECT_ZERO, BACKEND_FORGE, NET_ENGINEER, UI_ARTIST) und alte Struktur ohne Schichten, ohne Holschuld, ohne Evolutionsprinzip. | Veraltetes Dokument. Wer es liest, bekommt ein falsches Bild des Systems. |
| 1.4 | `docs/01_CORE_DNA/COMPRESSIVE_INTELLIGENCE.md` | (a) Abschnitt "Der Orchestrator (osmium-council)" korrigieren: Core Council ist NICHT der Orchestrator, sondern ein Sonderprotokoll/Ethikrat. Der Orchestrator ist Schicht 1. (b) Alte Rollennamen (Architect Zero etc.) durch generische Schicht-3-Bezeichnungen ersetzen oder als Beispiele kennzeichnen. (c) 3-Schichten-Modell als Organisationsstruktur ergaenzen. | Kernkonzept-Dokument verweist auf veraltete Struktur. Die Prinzipien (Vektor-Enge, Dissonanz, Boolean-Feedback) sind korrekt, aber die Rollenzuordnung stimmt nicht mehr. |

### PRIORITAET 2: HOCH (Fehlende Prinzipien in Agenten)

| # | Datei | Aenderung | Warum |
|---|-------|-----------|-------|
| 2.1 | Alle 11 Schicht-3 Agenten-MDs (siehe Liste unten) | Holschuld-Absatz hinzufuegen: "Du hast HOLSCHULD. Bevor du fehlende Information anforderst: Durchsuche Codebase, Docs, Skills, ChromaDB. Erst nach gruendlicher Suche: Anforderung an Teamleiter (1 Satz)." | Das Holschuld-Prinzip steht nur in `.cursorrules` und `team-lead.md`. Schicht-3-Agenten wissen nicht, dass sie Holschuld haben. |
| 2.2 | Alle 11 Schicht-3 Agenten-MDs | Evolutionsprinzip-Absatz hinzufuegen: "Antwort auf 'geht das?' ist IMMER ja – bis Beweis der harten Grenze (Physik, Stand der Technik, Hardware-Limit). 'Geht nicht weil API/SDK/Format/Zugang fehlt' = UNAKZEPTABEL." | Gleicher Grund: Nur in `.cursorrules` und `team-lead.md` definiert. |

**Betroffene Agenten-Dateien:**
- `.cursor/agents/virtual-marc.md`
- `.cursor/agents/nd-analyst.md`
- `.cursor/agents/nd-therapist.md`
- `.cursor/agents/system-architect.md`
- `.cursor/agents/db-expert.md`
- `.cursor/agents/security-expert.md`
- `.cursor/agents/api-interface-expert.md`
- `.cursor/agents/osmium-judge.md`
- `.cursor/agents/ux-designer.md`
- `.cursor/agents/universal-board.md`
- `.cursor/agents/osmium-council.md`

### PRIORITAET 3: MITTEL (Tote Features aktivieren / Konzepte dokumentieren)

| # | Datei | Aenderung | Warum |
|---|-------|-----------|-------|
| 3.1 | `src/api/routes/` (neuer Endpunkt oder Integration in bestehende Route) | `query_simulation_evidence()` in RAG-Pipeline einbinden: (a) API-Route `/api/simulation-evidence/query` erstellen, oder (b) in `llm_interface.py` als optionalen Kontext-Lieferant fuer Prompts einbauen | 28 Indizien liegen in ChromaDB als Dead Data. Ohne Query-Anbindung kann kein Agent und kein LLM darauf zugreifen. |
| 3.2 | `docs/01_CORE_DNA/RUECKWAERTSEVOLUTION.md` (NEU) | Neues Konzeptdokument: Rueckwaertsevolution als AGI-Genese formalisieren. Inhalt: (a) Definition (von fertiger Vision rueckwaerts zu implementierbaren Schritten), (b) Abgrenzung zu klassischem Wasserfall/Agile, (c) Wie es im CORE-System angewandt wird, (d) Verbindung zu Simulationstheorie-Indizien | Konzept existiert nur als Denkfigur, nicht als Systemdokument. Ohne Formalisierung kann kein Agent das Konzept anwenden. |
| 3.3 | `src/logic_core/bias_damper.py` | `context_injection_header` (Zeile 39-61): Klarstellung ergaenzen, dass Ring-0-Direktiven ein Cross-Cutting-Concern sind, der in allen 3 Schichten wirkt. Optional: Referenz auf das 3-Schichten-Modell hinzufuegen. | Vermeidet Verwirrung zwischen Ring-Modell (kognitive Sicherheit) und Schichten-Modell (Agentenkoordination). |
| 3.4 | `docs/01_CORE_DNA/stammdokumente_oc/02_MARC_UND_TEAM.md` | Alte Rollennamen und "Level 0" Referenzen aktualisieren | Konsistenz mit neuem Modell |

### PRIORITAET 4: NIEDRIG (Aufraeumen, Legacy-Bereinigung)

| # | Datei | Aenderung | Warum |
|---|-------|-----------|-------|
| 4.1 | `docs/01_CORE_DNA/osmium_council/*.md` (alte SKILL-Dateien) | Alle alten OC-Skill-Dateien (architect-zero, backend-build_engine, net-engineer, ui-artist, data-archivist, nt-specialist) pruefen und als DEPRECATED markieren oder loeschen. Die neuen Agenten-Definitionen liegen in `.cursor/agents/`. | Alte Dateien verwirren: Wer `docs/01_CORE_DNA/osmium_council/architect-zero/SKILL.md` liest, bekommt ein voellig anderes Bild als wer `.cursor/agents/system-architect.md` liest. |
| 4.2 | `docs/DOCS_INDEX.md` | Aktualisieren: Neue Dateien referenzieren (POST_ITERATION_ATLAS_CHANGES.md, OCBRAIN_VOLLINTEGRATION_PLAN.md, RUECKWAERTSEVOLUTION.md), alte Rollennamen entfernen | Index muss aktuell sein |
| 4.3 | `.cursor/skills/osmium-council/SKILL_OLD.md` | Loeschen oder archivieren (liegt bereits als Backup unter `backups/`) | Tote Datei, alte Struktur |
| 4.4 | `src/security/nt_mapping.py` | "Level 0" Referenzen pruefen und an 3-Schichten-Terminologie anpassen | Konsistenz |

---

## CROSS-CUTTING: Ring-0 vs. 3-Schichten – Koexistenz-Modell

Die Ring-0-Direktiven (BIAS_DEPTH_CHECK, NEGENTROPIE_CHECK, KONSTRUKTIVE_DISSONANZ, SCAFFOLDING) und das 3-Schichten-Modell sind **KEINE Konkurrenten**. Sie operieren auf verschiedenen Achsen:

```
3-SCHICHTEN-MODELL (Wer koordiniert wen?)
  Schicht 1: Orchestrator
  Schicht 2: Teamleiter
  Schicht 3: Produzenten + Auditoren

RING-0-DIREKTIVEN (Kognitive Sicherheit, Cross-Cutting)
  ├─ Wirken INNERHALB jeder Schicht
  ├─ BIAS_DEPTH_CHECK: Schuetzt vor Hyper-Fokus-Schleifen (alle Schichten)
  ├─ NEGENTROPIE_CHECK: Verhindert Stagnation (alle Schichten)
  ├─ KONSTRUKTIVE_DISSONANZ: Echokammer-Bremse (alle Schichten)
  └─ SCAFFOLDING: Autonomie-Foerderung statt Abhaengigkeit (alle Schichten)
```

**Aktion:** Dieses Koexistenz-Modell muss in PROMPT_B (Prio 1.1) und bias_damper.py (Prio 3.3) explizit dokumentiert werden.

---

## ZUSAMMENFASSUNG

| Prioritaet | Anzahl Aenderungen | Aufwand (geschaetzt) |
|---|---|---|
| P1 KRITISCH | 4 Dateien | 2-3h (PROMPT_B ist komplex) |
| P2 HOCH | 11 Agenten-Dateien | 1h (Template-basierte Ergaenzung) |
| P3 MITTEL | 4 Dateien/Features | 3-4h (RAG-Integration + neues Dokument) |
| P4 NIEDRIG | 4 Dateien | 30min (Bereinigung) |
| **GESAMT** | **~23 Dateien** | **~7-8h** |

---

## NICHT-AENDERUNGEN (Bewusst beibehalten)

- **`bias_damper.py` Ring-0-Logik:** Code ist korrekt und konsistent. Die Ring-0-Checks (bias_depth_check, negentropy_check) sind valide kognitive Sicherheitsmechanismen. Nur die Dokumentation/Terminologie muss klarstellen, dass Ring-0 kein Hierarchie-Level ist.
- **`negentropy_check.py`:** Vollstaendig korrekt und schichtenunabhaengig. Keine Aenderung noetig.
- **`secrets_loader.py`:** Korrekt implementiert. Holschuld/Evolutionsprinzip nicht relevant fuer Security-Module.
- **`chroma_client.py`:** Infrastruktur-Code ist korrekt. Die fehlende Nutzung von `query_simulation_evidence()` ist eine Pipeline-Luecke, kein Client-Problem.
- **`.cursorrules`:** Bereits aktuell. Bildet die Single Source of Truth fuer das 3-Schichten-Modell.
- **`team-lead.md`:** Bereits aktuell. Vollstaendig konsistent mit `.cursorrules`.
- **`virtual-marc.md`:** Weitgehend aktuell. Braucht nur Holschuld + Evolutionsprinzip (P2).
- **`osmium-council.md`:** Weitgehend aktuell als Sonderprotokoll. Braucht nur Holschuld + Evolutionsprinzip (P2).
