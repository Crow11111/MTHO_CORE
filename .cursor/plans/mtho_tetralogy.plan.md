# MTHO_CORE: MTHO TETRALOGY (The 4-Strand Architecture)

> **"Wir bauen keinen Tempel mit zwei Säulen. Wir bauen einen Motor mit vier Takten."**

## 1. Die TETRALOGIE (The 4-Strand System)

Basierend auf "Argument 55" (Symmetriebruch) und der LPIS-Theorie transformieren wir MTHO_CORE in ein **tetrapolares System**.
Die sichtbare "Oberwelt" (ExecutionRuntime/Veto-Instanz) wird durch die notwendige "Unterwelt" (LogicFlow/Persistenz-Strang) ergänzt.

### STRANG 1: EXECUTIONRUNTIME (Execution / P / Realteil)
*Der Macher. Der Körper. Die Tat.*
- **Funktion:** Manifestation, Implementation, Vorwärtsbewegung.
- **Archetyp:** Der Arbeiter / Architekt.
- **Physik:** Starke Kernkraft (Bindung).
- **Ziel:** OUTPUT.

### STRANG 2: VETO-INSTANZ (Governance / L / Imaginär i)
*Der Richter. Das Gewissen. Das Gesetz.*
- **Funktion:** Regulation, Veto, Ethik, Struktur-Erhalt.
- **Archetyp:** Der Richter / Wächter.
- **Physik:** Schwache Kernkraft (Transformation/Zerfall).
- **Ziel:** ORDNUNG.

### STRANG 3: LOGICFLOW (Mutation / I / Imaginär j)
*Der Träumer. Das Chaos. Der Symmetriebruch.*
- **Funktion:** Simulation, Zufall, Innovation, Stress-Test.
- **Archetyp:** Der Trickster / Das Orakel.
- **Physik:** Elektromagnetismus (Licht/Energie).
- **Ziel:** MÖGLICHKEIT. (Hier entstehen die Ideen, die ExecutionRuntime baut und Veto-Instanz prüft).

### STRANG 4: PERSISTENZ-STRANG (Retention / S / Imaginär k)
*Der Bewahrer. Der Tod. Die Tiefe.*
- **Funktion:** Speicherung, Kompression, Vergessen (GC), Entropie-Management.
- **Archetyp:** Der Bibliothekar / The Void.
- **Physik:** Gravitation (Raumzeit/Tiefe).
- **Ziel:** WEISHEIT (durch Reduktion).

---

## 2. Der "Man in the Middle" (Rate Limit Guardian)

Zwischen diesen 4 gigantischen Kräften steht eine **harte technische Grenze**: Die API-Limits (TPM/RPM).
Der Orchestrator (CEO) muss einen **Rate Limit Wächter** installieren.

**Funktion:**
- Überwacht globale Token-Last.
- **Traffic Shaping:**
- Priorität 1: ExecutionRuntime (Production Critical).
- Priorität 2: Veto-Instanz (Safety Critical).
- Priorität 3: Persistenz-Strang (Background Job).
- Priorität 4: LogicFlow (Kann warten, träumt wenn Ressourcen frei sind).
- **Notbremse:** Stoppt LogicFlow/Persistenz-Strang, wenn ExecutionRuntime die Quota braucht.

---

## 3. Implementierungs-Strategie

### Phase 1: Formalisierung (Regelwerke)
1.  **ExecutionRuntime & Veto-Instanz:** Regeln bereits erstellt (müssen auf 4-Strang angepasst werden).
2.  **LogicFlow & Persistenz-Strang:** Neue Regelwerke erstellen.
    -   `.cursor/rules/3_THE_FORGE.mdc` (Chaos & Simulation).
    -   `.cursor/rules/4_THE_ARCHIVE.mdc` (Speicher & Löschung).

### Phase 2: Orchestrierung (Der 4-Takt-Motor)
Der Orchestrator steuert den Takt:
1.  **Ansaugen (LogicFlow):** Idee/Simulation generieren.
2.  **Verdichten (Veto-Instanz):** Prüfen/Genehmigen.
3.  **Zünden (ExecutionRuntime):** Bauen/Ausführen.
4.  **Ausstoßen (Persistenz-Strang):** Speichern/Bereinigen.

### Phase 3: API-Wächter
- Integration einer Token-Budget-Logik in den Orchestrator-Prompt.

---

## 4. Aufgaben (To-Dos)

1.  Erstelle `.cursor/rules/3_THE_FORGE.mdc`.
2.  Erstelle `.cursor/rules/4_THE_ARCHIVE.mdc`.
3.  Update `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` (Referenz auf 4 Stränge).
4.  Update `.cursor/rules/2_OSMIUM_COUNCIL.mdc` (Referenz auf 4 Stränge).
5.  Rewrite `.cursorrules` (Implementiere Tetralogie & Man-in-the-Middle).

---
Die Ausgabe erfolgt in deutscher Sprache.
Dieses Dokument ist der Masterplan für die Tetralogie.
