<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# POST-ITERATION CURSOR CHANGES – Konsistenz-Audit

**Datum:** 2026-03-01  
**Kontext:** Nach Iterationssprung – Produktivumgebung Cursor IDE  
**Referenz:** .cursorrules v2.0, team-lead.md, 3-Schichten-Modell

---

## 1. ZUSAMMENFASSUNG

| Kriterium | Status | Betroffene Agenten |
|-----------|--------|--------------------|
| Budget-Constraint Block | ✅ Alle vorhanden | – |
| expertise/* Skill-Referenz | ⚠️ 2 ohne, 8 korrekt | osmium-judge, universal-board |
| Holschuld-Prinzip | ❌ Keiner hat es | Alle 10 Schicht-3-Agenten |

**Schicht-3-Agenten (10):** api-interface-expert, db-expert, nd-analyst, nd-therapist, osmium-judge, security-expert, system-architect, universal-board, ux-designer, virtual-marc  
**Ausgenommen:** team-lead (Schicht 2), osmium-council (Sonderprotokoll)

---

## 2. INKONSISTENZEN (Datei + Problem)

### 2.1 Holschuld-Prinzip fehlt bei allen Schicht-3-Agenten

**Problem:** Laut .cursorrules §7 hat jeder Agent eine Holschuld. Der team-lead hat das explizit; kein Schicht-3-Agent erwähnt es.

**Betroffene Dateien:**
- `.cursor/agents/api-interface-expert.md`
- `.cursor/agents/db-expert.md`
- `.cursor/agents/nd-analyst.md`
- `.cursor/agents/nd-therapist.md`
- `.cursor/agents/osmium-judge.md`
- `.cursor/agents/security-expert.md`
- `.cursor/agents/system-architect.md`
- `.cursor/agents/universal-board.md`
- `.cursor/agents/ux-designer.md`
- `.cursor/agents/virtual-marc.md`

**Referenz (.cursorrules §7):**
> Niemand im System hat eine Bringschuld. Jeder Agent hat eine **Holschuld**.
> 1. Agent (Schicht 3) braucht Information → Agent sucht SELBST (Codebase, Docs, Skills, ChromaDB)
> 2. Agent findet nichts → Agent fordert beim Teamleiter an
> 3. VERBOTEN: "Ich kann den Plan nicht erstellen weil mir Information X fehlt" als Endantwort.

---

### 2.2 Kein expertise/* Skill bei osmium-judge

**Problem:** osmium-judge referenziert keinen expertise-Skill. Als generischer Logik-Auditor kann das fachlich passen; für Security- oder Architektur-Reviews wäre z.B. `expertise/security` oder `expertise/networking` sinnvoll.

**Betroffene Datei:** `.cursor/agents/osmium-judge.md`

---

### 2.3 Kein expertise/* Skill bei universal-board

**Problem:** universal-board referenziert keinen expertise-Skill. Als Ressourcen-/Ethik-Auditor gibt es keinen passenden expertise-Skill (planning/* ist für Teamleiter). Kann so bleiben oder später `expertise/` um Risiko/Kosten erweitern.

**Betroffene Datei:** `.cursor/agents/universal-board.md`

---

### 2.4 system-architect: Einzelner Skill

**Status:** Referenziert nur `expertise/networking`. Für Architektur-Reviews sind ggf. auch database, security relevant. Da „lade nur bei Bedarf“ gilt, ist ein primärer Skill ausreichend – keine Änderung nötig.

---

## 3. VORGESCHLAGENE FIXES

### Fix 1: Holschuld-Block für alle Schicht-3-Agenten

**Einheitlicher Block (nach Budget-Constraint einfügen):**

```markdown
**Holschuld:** Du hast KEINE Bringschuld. Brauchst du Information → such selbst (Codebase, Docs, Skills, ChromaDB). Erst wenn du gruendlich gesucht hast und nichts findest → Anforderung an Teamleiter (1 Satz). VERBOTEN: "Geht nicht weil X fehlt" als Endantwort ohne vorherige Suche.
```

**Einfügeposition:** Direkt nach dem Budget-Constraint-Block, vor der Skill-Referenz (falls vorhanden).

---

### Fix 2: osmium-judge – optionale Skill-Referenz

**Option A (minimal):** Keine Änderung – generischer Auditor ohne festen Skill.

**Option B (empfohlen):** Hinweis auf bedarfsweise Skills ergänzen:

```markdown
Verfuegbare Fach-Skills (bei Bedarf): `.cursor/skills/expertise/security/SKILL.md`, `.cursor/skills/expertise/networking/SKILL.md` – lade nur wenn Review-Domäne es erfordert.
```

---

### Fix 3: universal-board – keine Änderung

Kein passender expertise-Skill vorhanden. Bei späterer Erweiterung um `expertise/risk` oder ähnlich könnte referenziert werden.

---

## 4. PRÜFMATRIX (Vor/Nach Fix)

| Agent | Budget | expertise/* | Holschuld |
|-------|--------|-------------|-----------|
| api-interface-expert | ✅ | ✅ networking | ❌ → Fix 1 |
| db-expert | ✅ | ✅ database | ❌ → Fix 1 |
| nd-analyst | ✅ | ✅ ai-integration | ❌ → Fix 1 |
| nd-therapist | ✅ | ✅ ai-integration | ❌ → Fix 1 |
| osmium-judge | ✅ | ⚠️ fehlt | ❌ → Fix 1, Fix 2 optional |
| security-expert | ✅ | ✅ security | ❌ → Fix 1 |
| system-architect | ✅ | ✅ networking | ❌ → Fix 1 |
| universal-board | ✅ | ⚠️ N/A | ❌ → Fix 1 |
| ux-designer | ✅ | ✅ ui-design | ❌ → Fix 1 |
| virtual-marc | ✅ | ✅ ai-integration | ❌ → Fix 1 |

---

## 5. VERIFIZIERTE REFERENZEN

- **.cursorrules:** 3-Schichten-Modell, Holschuld §7, Nein-bis-zur-harten-Grenze §8, Skill-Lade-Logik §5
- **team-lead.md:** Holschuld, Nein-bis-zur-harten-Grenze, Budget-Constraints, Tokendruck-Steuerung
- **virtual-marc.md:** Schicht 3 mit Sonderstatus, Budget-Constraint, expertise ai-integration
- **osmium-council.md:** Sonderprotokoll außerhalb der Hierarchie
- **expertise-Skills:** ai-integration, database, networking, security, ui-design – alle vorhanden

---

## 6. NÄCHSTE SCHRITTE

1. Fix 1 in alle 10 Schicht-3-Agenten einarbeiten (Holschuld-Block).
2. Fix 2 für osmium-judge optional umsetzen.
3. Nach Änderungen: kurze Stichprobe, ob Agenten-Prompts noch lesbar und konsistent sind.
