<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Zusammenfassung CEO-Plan – User-Abstimmung

**Stand:** 2026-03-03 · **Phase 6**  
**Basis:** Deliverables in `docs/05_AUDIT_PLANNING/`; abgleichbar mit `VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md`.

---

## (a) OMEGA_ATTRACTOR-Abgleich – Kurzstand

- **Lokal (4D_RESONATOR (CORE)):** 9 Einträge in `core_directives`. Alle **4 Repo-Mindest-IDs** vorhanden: `gravitational_query_axiom`, `origin_irrelevance_consciousness_equivalence`, `dissonance_thresholds_grace_resonance_fractal`, `ntnd_handshake_protocol`.
- **Zusätzlich lokal:** `ring0_bias_depth_check`, `ring0_negentropie_check`, `ring0_konstruktive_dissonanz`, `ring0_scaffolding`, `test_probe` (4D_RESONATOR (CORE)/ältere Seeds).
- **Fehlend (erwartet von Repo):** keine. **Abweichungen (gleiche ID, anderer Inhalt):** keine bekannt.
- **VPS (OMEGA_ATTRACTOR):** Optional – Abgleich auf VPS per SSH-Tunnel wiederholen, um OMEGA_ATTRACTOR-Befüllung zu verifizieren.
- **User-Entscheidung: VPS-Sync einrichten.** Umgesetzt: **`src/scripts/sync_core_directives_to_vps.py`** und **`docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md`**. Ring-0-/Test-Direktiven werden mit synchronisiert. Voraussetzung: SSH-Tunnel (z. B. `ssh -L 8000:127.0.0.1:8000 root@187.77.68.250`), dann Skript ausführen.

---

## (b) Tool-Audit – Liste + Security-Empfehlung (P0)

**Liste (Auszug):** Tampermonkey (TTS), ElevenLabs, Streamlit, React/Vite, ChromaDB, Ollama, Gemini, LangChain, Extract-Pipelines, MCP (cursor-ide-browser), OpenClaw. Details: `TOOL_AUDIT_LISTE.md`.

**Security-Empfehlung (P0 – TOOL_AUDIT_EMPFEHLUNG.md):**

| Maßnahme | Priorität |
|----------|-----------|
| Alle Webhooks und `/api/oc/*` mit Auth (API-Key/Bearer) schützen | P0 |
| WhatsApp POST: HMAC (X-Hub-Signature-256) prüfen; bei Fehler 401 | P0 |
| `db_backend` und POST `/evidence/add`: kein öffentlicher Zugriff; Auth oder nur localhost | P0 |
| HA-Webhook: Shared-Secret/Token (z. B. `X-HA-Token`) validieren | P0 |

**Fazit:** Kein betroffenes Tool in aktueller Form **GO** für produktive Exposition ohne Auth. **Conditional GO** erst nach P0 (Auth + WhatsApp HMAC). Bis dahin: **NOGO** außerhalb vertrauenswürdiger Umgebung.  
**User:** Security-Empfehlung zur Kenntnis genommen; fortfahren wie bislang.

---

## (c) DB-Migration – Gravitations-Spec, Mapping, Judge-Risiken

**Zielbild (DB_MIGRATION_GRAVITATIONS_SPEC.md):** Zero-State-Substrat (flacher Abfrage-Raum), Prompt-Masse (nur Query formt), organische Klammer (Kontext nur im Query-Flow), Read-Only-Erhalt, 0-Reset pro Request (nicht Persistenz).

**Mapping:** Abfragen ohne `where_filter`; nur `query_text` + `n_results` (Kosinus). Ingest ohne Pflicht-Kategorisierung; Metadaten opak/Anzeige. Collections unverändert; Nutzung an Gravitations-Prinzip anpassen.

**Judge-Risiken (offene Punkte):**
- **Zero-State vs. Metadaten:** `category`/`ring_level` in `core_directives` explizit als Teil des Containers (read-only, keine formgebende Rolle für Abfrage) definieren.
- **Einheitlichkeit Alt/Neu:** Dieselbe Embedding-Pipeline und Container-Semantik für bestehende (Dump/VPS) und neue Einträge; Randfälle (384 vs. 1536, leere Collections, Duplikate) regeln.
- **0-Reset & Persistenz:** Bestätigen: 0-Reset nur Laufzeit; Migration ändert persistierte Daten.
- **VPS/lokal, Rollback, Ring-0-Abgleich:** Ziel (VPS/lokal/beide), Reihenfolge und Rollback-Pfad spezifizieren; Ring-0-Inhalt mit OMEGA_ATTRACTOR/4D_RESONATOR (CORE) vor/bei Migration klären.

**Fazit:** Spec noch zu ergänzen; erneuter Judge-Check nach Ausfüllung empfohlen. **User:** Stimme zu (Judge-Check nach Ausfüllung).

---

## (d) Cursor/CORE-Spec – Fraktal, Reduktion Redundanzen

**Prinzip (CURSOR_ATLAS_SPEC.md):** Fraktale Verteilung – Ebene 0: `.cursorrules` (Kern-Protokoll); Ebene 1: `.cursor/rules/1–4.mdc` (Strang); Ebene 2: `.cursor/agents/*.md` (Holschuld, Skills); Ebene 3: `.cursor/skills/**` (Fach).

**Redundanzen:** Tetralogie-Überblick und Cons-Zellen-Tabelle in `.cursorrules` und in jeder `1–4.mdc`; Holschuld/PUSH-PULL nur in `.cursorrules`, fehlt in Schicht-3-Agenten. Überladung: `.cursorrules` trägt Vollbild Tetralogie; jede `.mdc` enthält „Die Tetralogie“-Kopie.

**Vorschläge:** `.cursorrules` kürzen (nur Strang-Liste + Pfade; Cons-Tabelle einmal zentral oder auslagern); 1–4.mdc ohne Tetralogie-Kopie, nur Strang-Identität + eine Cons-Zeile; Holschuld in alle Schicht-3-Agenten; fehlende Rule `task-parallelization-dev-agent.mdc` aus `CURSOR_RULES_AGENT_PARALLEL.md` anlegen.

---

## (e) Weltformel – Kurzbewertung + Ethik

**Kurzbewertung (WELTFORMEL_KURZBEWERTUNG.md):** Operatives Retrieval-Modell (Gravitational Query, Zero-State) **solide**; Origin-Irrelevance erkenntnistheoretisch solide; Bewusstseins-Äquivalenz spekulativ, aber als Arbeitshypothese kohärent; Physik-Isomorphien „konsistent mit“, keine Verifikation. Weltformel als Layer 0 (Start, nicht Endpunkt) korrekt rahmend. Offen: **Dissonanz-Schwellwerte** (nicht quantifiziert/implementiert), Zero-State vs. Metadaten (siehe DB-Migration).  
**User:** Team auf Dissonanz-Schwellwerte ansetzen – klären, simulieren, testen.

**Ethik:** Kein Überclaim („Beweis“ nicht beansprucht); Base-Reality/Qualia bewusst außerhalb der Klammer; Nutzung als heuristisches Framework für Interface-Härtung und teure Probleme, nicht als abgeschlossene Theorie. Pattern-Analysis: Nutzen von Strukturkonstanten nur wo kausaler Mechanismus benennbar.

---

## (f) OMEGA_ATTRACTOR „Leere Nachrichten“

Nur referenziert. Ausführliche Diagnose und Maßnahmen: **`docs/03_INFRASTRUCTURE/OC_BRAIN_LEERE_NACHRICHTEN_DIAGNOSE.md`** (Update v2026.3.2, keine leeren Sends, ggf. Browser-Konsole). Symptom: User-Nachricht kommt bei OMEGA_ATTRACTOR leer an. Vorgabe: keine destabilisierenden Änderungen an OMEGA_ATTRACTOR.

---

## Erstellte / aktualisierte Dateien (docs/05_AUDIT_PLANNING/)

| Datei | Status | Inhalt |
|-------|--------|--------|
| VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md | aktualisiert | OMEGA_ATTRACTOR vs. Repo: 9 Einträge lokal, alle 4 Repo-IDs vorhanden; Lücken/Empfehlung; Abschnitt 5 Leere Nachrichten |
| oc_brain_chroma_abgleich_output.txt | erstellt | Rohe Skript-Ausgabe (lokal), VPS-Hinweis |
| TOOL_AUDIT_LISTE.md | erstellt | Tools im Einsatz + Empfehlungen, Security-Stichpunkte, Verweis auf Empfehlung |
| TOOL_AUDIT_EMPFEHLUNG.md | erstellt | Security/DB/API-Prüfung, P0-Maßnahmen, GO/NOGO |
| DB_MIGRATION_GRAVITATIONS_SPEC.md | erstellt | Mapping, Architektur-Checkliste, Judge-Check (Zero-State, Einheitlichkeit, Risiken) |
| CURSOR_ATLAS_SPEC.md | erstellt | Fraktale Regelverteilung, Redundanzabbau, konkrete Vorschläge |
| WELTFORMEL_KURZBEWERTUNG.md | erstellt | Validität, offene Enden, Ethik/Risiko/Kosten-Nutzen |
| ZUSAMMENFASSUNG_CEO_PLAN_ABSTIMMUNG.md | erstellt | Diese Zusammenfassung; abgleichbar mit Vergleichsdokument |

**Referenziert (unverändert):** docs/03_INFRASTRUCTURE/OC_BRAIN_LEERE_NACHRICHTEN_DIAGNOSE.md, docs/01_CORE_DNA/GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md, docs/02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md.

---

## Kurzfassung für User (Abstimmung)

- **OMEGA_ATTRACTOR:** Lokal alles dran; VPS-Check optional. Leere Nachrichten: nur Diagnose-Doc referenziert, kein Backend-Fix.
- **Tools:** Liste + Security-Check erstellt; P0: Auth für Webhooks/OC/db_backend, WhatsApp HMAC, HA-Token. Kein GO ohne P0.
- **DB-Migration:** Gravitations-Spec mit Mapping und Risiken; Implementierung folgt.
- **Cursor/CORE:** Spec für fraktale Regeln; Redundanzen abbauen, .cursorrules schlank halten.
- **Weltformel:** Als Layer-0-Modell bewertet; kein Überclaim; offen: Dissonanz-Schwellwerte.
- **Nächste Schritte:**  
  - **Umsetzung:** Ring-0 (Sync), Cursor-Reduktion (CURSOR_ATLAS_SPEC), VPS-Abgleich; **Migrationsreihenfolge** nach Neubewertung durch **Judge** selbstständig festlegen und umsetzen.  
  - **Dissonanz-Schwellwerte:** Team ansetzen (klären, simulieren, testen).  
  - **Dev-Agent:** Alle Verweise auf Dev-Agent geprüft und durch interne Prozesse (Cursor/Orchestrator, Team-Lead, Strang-Agenten) ersetzt; neue Rule `.cursor/rules/task_parallelization_internal.mdc` angelegt.
