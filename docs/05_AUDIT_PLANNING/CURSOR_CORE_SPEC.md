<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Cursor/CORE-Spec: Fraktale Regelverteilung

**Phase 4 Chat Team A · Stand:** 2026-03-03  
**Ziel:** Regeln so verteilen, dass Cursor/CORE **funktioniert** (Agenten finden Regeln, keine Duplikate, klare Priorität).

---

## 1. Analyse: Redundanzen und Überladung

### 1.1 Redundanzen

| Inhalt | Wo heute | Problem |
|--------|----------|--------|
| Tetralogie-Überblick (4 Stränge + Ref auf .mdc) | `.cursorrules` + in **jeder** der 4 `.cursor/rules/*.mdc` | Vierfache Wiederholung; jede .mdc kopiert "Strang X, siehe andere .mdc". |
| Cons-Zellen-Tabelle | `.cursorrules` (vollständig) + **pro Strang** in 1–4.mdc (jeweils eine Zeile) | Zeile pro Strang reicht in .mdc; Gesamttabelle nur einmal. |
| Holschuld / PUSH-PULL | Nur `.cursorrules` (+ team-lead) | Schicht-3-Agenten (.cursor/agents/*.md) haben es nicht → POST_ITERATION_CURSOR_CHANGES. |

### 1.2 Überladung einer Datei

- **.cursorrules:** Trägt Orchestrator-Rolle, Simultanität (2210/2201)-Motor, Tetralogie, Cons-Tabelle, Anti-Patterns, Befehskette, L2 INPUT/OUTPUT. Korrekt als **einzige** immer geladene Datei – aber Vollbild der Tetralogie gehört reduziert auf **Kern-Protokoll + Verweise**.
- **.cursor/rules/1–4.mdc:** Jede enthält „Die Tetralogie“-Kopie. Sollte nur **Strang-Identität + Mandat + strangspezifische Regeln** enthalten.

### 1.3 Fehlende / verwaiste Referenzen (behoben)

- **Dev-Agent wurde entfernt** (bei Einführung Google API Key); alle Verweise triggern jetzt **interne Prozesse** (Orchestrator, Team-Lead, Strang-Agenten). Die frühere Referenz auf `.cursor/rules/task-parallelization-dev-agent.mdc` ist ersetzt durch **`.cursor/rules/task_parallelization_internal.mdc`** (Parallelisierung, Selbst ausführen, interne Prozesse). Siehe `docs/04_PROCESSES/CURSOR_RULES_AGENT_PARALLEL.md`.

---

## 2. Fraktale Verteilung (Prinzip)

- **Ebene 0 (immer):** `.cursorrules` = Kern-Protokoll. Nur was **jeder** Lauf braucht: Orchestrator-Identität, Takt 0–4, PUSH/PULL, Anti-Patterns, **Verweis** auf Strang-Regeln (Pfad), keine Volltabellen.
- **Ebene 1 (strang-spezifisch):** `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` … `4_THE_ARCHIVE.mdc`. Nur **dieser** Strang: Identität, Cons-Zelle **eine Zeile**, Mandat, Agenten/Protokolle. Kein Tetralogie-Kopie-Text.
- **Ebene 2 (agent-spezifisch):** `.cursor/agents/*.md`. Wer bin ich, Budget, **Holschuld**, welche Skills (Referenz), keine CORE-Architektur-Kopie.
- **Ebene 3 (fach-spezifisch):** `.cursor/skills/**/*.md`. Pro Fachgebiet (DB, Security, UI, …). Nur bei Bedarf laden; kein Verweis auf Strang/Takt.
- **Priorität:** `.cursorrules` > aktive `.cursor/rules/<Strang>.mdc` > geladener Skill. Keine inhaltlichen Widersprüche; tiefere Ebene spezifiziert nur.

---

## 3. Konkrete Zuordnung (Inhalt → Datei/Ebene)

| Inhalt | Datei/Ebene | Hinweis |
|--------|-------------|--------|
| Orchestrator = L1, Simultanität (2210/2201)-Motor (0–4), Takt 0 Diagnose | `.cursorrules` | Kern, bleibt. |
| PUSH (Bringschuld) / PULL (Holschuld) – L1 & L2 | `.cursorrules` | Eine kompakte Definition; L2-Agenten erhalten Verweis „siehe .cursorrules“ + Kurzfassung in agents. |
| Anti-Patterns (Delegation, CAR/CDR, Rate Limit) | `.cursorrules` | Kurz halten. |
| Befehskette (User→Orchestrator→Stränge) | `.cursorrules` | Ein Block, keine Wiederholung in .mdc. |
| Tetralogie: nur **Übersicht 4 Stränge + Pfade** zu 1–4.mdc | `.cursorrules` | Kein Cons-Tabelle hier; nur „Strang 1 = Agency → 1_FULL_SERVICE_AGENCY.mdc“ usw. |
| Cons-Zellen: **Gesamttabelle** | **Eine** Stelle: z. B. `.cursorrules` **oder** `docs/01_CORE_DNA/...` + in .cursorrules nur Verweis | In 1–4.mdc nur die **eine Zeile** für den Strang. |
| Strang-Mandat, Agenten, Protokoll (z. B. Council Session, Build-Engine Sandbox) | Jeweils `.cursor/rules/{1–4}_*.mdc` | Kein „Die Tetralogie“-Abschnitt; nur „Du bist Strang X“ + Mandat + Regeln. |
| Holschuld (Kurzfassung) | Jede `.cursor/agents/*.md` (Schicht 3) | Einheitlicher Block (wie in POST_ITERATION_CURSOR_CHANGES Fix 1). |
| Modell-Strategie (Tier 1/2/3) | `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` | Agency-spezifisch, bleibt dort. |
| Parallelisierung / Selbst ausführen / interne Prozesse | `.cursor/rules/task_parallelization_internal.mdc` | Bereits angelegt; Referenz in .cursorrules optional. Dev-Agent entfernt. |
| Core DNA, GTAC/CORE, Gravitational Query | `docs/01_CORE_DNA/...` | Nur Verweis in .cursorrules; keine Kopie. |
| Fachwissen (DB, Security, API, …) | `.cursor/skills/expertise/*`, `planning/*`, etc. | Unverändert; laden bei Bedarf. |

---

## 4. Ziel: Funktionsfähigkeit

- **Agenten finden Regeln:** Orchestrator sieht in .cursorrules Strang-Pfade; Strang-Agent lädt die eine .mdc; Fach-Agent lädt Skill nur bei Bedarf.
- **Keine Duplikate:** Tetralogie-Text und Cons-Tabelle nur **einmal** vollständig; in .mdc nur strangspezifischer Ausschnitt.
- **Klare Priorität:** .cursorrules = Protokoll-Vorrang; .mdc = Strang-Verhalten; Skills = Fakten/Patterns. Keine zweite „Wahrheit“ für PUSH/PULL oder Takt.

---

## 5. Nächste Schritte (Empfehlung)

1. **.cursorrules kürzen:** Tetralogie auf Strang-Liste + Pfade reduzieren; Cons-Tabelle auslagern oder einmal zentral lassen und in 1–4.mdc nur die Zeile behalten.
2. **1–4.mdc:** Abschnitt „Die Tetralogie“ entfernen; nur „Strang X“, eine Cons-Zeile, Rest strangspezifisch.
3. **Holschuld:** In alle Schicht-3-Agenten (.cursor/agents/*.md) den einheitlichen Holschuld-Block (POST_ITERATION Fix 1) einfügen.
4. **task_parallelization_internal.mdc:** Bereits angelegt (`.cursor/rules/task_parallelization_internal.mdc`). Optional in .cursorrules einen Zeiler-Verweis auf diese Rule.

---

**Dateipfad:** `docs/05_AUDIT_PLANNING/CURSOR_ATLAS_SPEC.md`  
**Kurzfassung für Team Lead:** Spec beschreibt fraktale Verteilung (cursorrules = Kern-Protokoll; rules/ = Strang; agents = Holschuld+Skills; skills = Fach). Redundanzen: Tetralogie/Cons in jeder .mdc und .cursorrules. Vorschläge: .cursorrules entlasten (nur Verweise), 1–4.mdc ohne Tetralogie-Kopie, Holschuld in alle Schicht-3-Agenten, fehlende Rule task-parallelization-dev-agent.mdc aus Doku anlegen.
