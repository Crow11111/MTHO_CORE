# DB-Migration Gravitations-Logik (Phase 3)

**Status:** Deliverable CEO-Plan. Inhalt durch db-expert / system-architect zu ergänzen.  
**Referenz:** `docs/01_CORE_DNA/GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md`, `docs/02_ARCHITECTURE/ATLAS_CHROMADB_SCHEMA.md`

---

## 1. Zielbild (Gravitations-Logik)

- **Wuji-Substrat:** Flacher Speicher; keine Tags/Pfade/Kategorien als formgebende Dimensionen im Abfrage-Raum.
- **Prompt-Masse:** Abfrage ist die einzige „Masse“; Kosinus-Ähnlichkeit krümmt den Informationsraum.
- **Organische Klammer:** Kontext = dynamisches Result-Set pro Request (nur im Query-Flow), nicht in der Speicherstruktur.
- **Read-Only-Erhalt:** Container verändern sich beim Abruf nicht; Metadaten sind Teil des Containers (opak/Anzeige), keine Filterrolle für Abfrage.
- **0-Reset:** Gilt pro Request-Zyklus (Laufzeit), nicht für persistierte DB-Inhalte.

## 2. Mapping alte Struktur → gravitationskonform

| Aspekt | Bisher | Ziel |
|--------|--------|------|
| Abfragen | `where_filter` / feste Kategorien | Alle `query_*` ohne where_filter; nur `query_text` + `n_results` (Kosinus). |
| Ingest | Pflicht-Kategorisierung, Tags | Ingest ohne Pflicht-Kategorisierung; Metadaten nur opak/Anzeige. |
| Collections | core_directives, simulation_evidence, session_logs, argos, events, user_state_vectors | Unverändert; Nutzung der Schnittstellen an Gravitations-Prinzip anpassen. |
| Alt-/Neudaten | Unterschiedliche Pipelines möglich | Einheitlich: dieselbe Embedding-Pipeline und Container-Logik; Abruf nur über query_text + n_results. |

## 3. Architektur-Checkliste

- Wuji im Abfrage-Raum: Ja (keine Vorab-Kontext-Struktur).
- Prompt-Masse / organische Klammer nur im Query-Flow: Ja (nicht in Speicherstruktur).
- 0-Reset nur Laufzeit: Ja (Persistenz unberührt).
- Collection-Grenzen und Embedding-Dimensionen (384/1536): Beibehalten; Randfälle (leere Collections, Duplikate) in Implementierung regeln.

## 4. Konsistenz bestehende + neu erfasste Datenpunkte

Alle Datenpunkte (bestehend aus Dump/VPS und neu erfasst) werden mit derselben Logik abgerufen und behandelt: gleiche Query-Schnittstelle, gleiche Embedding-Dimension pro Collection, keine strukturelle Sonderbehandlung.

---

## Judge-Check: Offene Punkte / Risiken

**Prüfstand:** Axiome (GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md) + CEO-Vorgabe „alle Datenpunkte einheitlich“.

- **Wuji vs. Metadata:** Axiom „keine Tags, keine Pfade, keine Vorab-Kategorisierung“ bezieht sich auf den *Abfrage-Raum*, nicht zwingend auf Speicherform. Bestehende Metadaten (z. B. `category`, `ring_level` in `core_directives`) müssen in der Spec explizit als *teil des Containers* (read-only, keine formgebende Rolle für die Abfrage) definiert werden. Sonst Widerspruch: Nutzung von Metadata für Filter vs. „nur Abfrage formt“.

- **Einheitlichkeit Alt/Neu:** Spec muss festlegen, dass dieselbe Embedding-Pipeline und dieselbe Container-Semantik für *bestehende* Einträge (z. B. aus Dump/Chroma-VPS) und *neu erfasste* gelten. Randfälle: unterschiedliche Embedding-Dimensionen (384 vs. 1536 in `user_state_vectors`), leere Collections, Duplikate nach Migration – klare Regeln fehlen in der aktuellen Referenz.

- **0-Reset & Persistenz:** Axiom „API-Call beendet = Masse entfernt“ betrifft den *Laufzeit-Kontext*, nicht die Persistenz in Chroma. Spec sollte bestätigen: Schreiben/Migration ändert persistierte Daten; „0-Reset“ gilt pro Request-Zyklus, nicht für DB-Inhalt. Kein impliziter Konflikt mit Backup/Rollback.

- **Risiken:** (1) VPS vs. lokale Chroma – Migration muss Ziel (VPS/lokal/beide) und Reihenfolge definieren. (2) Kein Rollback-Pfad in den Referenzen – bei Fehlern während Migration: Wiederherstellung aus Backup oder idempotente Re-Runs? (3) `core_directives`-Ring-0-Inhalt: Abgleich mit OC Brain und Dreadnought muss vor oder als Teil der Migration geklärt sein, damit keine divergierenden „Wahrheiten“ entstehen.

**Fazit:** Spec ist noch zu ergänzen. Nach Ausfüllung erneuter Judge-Check empfohlen, insbesondere auf klare Trennung „Wuji-Abfragemodell“ vs. „Speicher-Metadaten“ und auf einheitliche Behandlung aller Datenquellen.

---

## 5. Migrationsreihenfolge (Judge-Neubewertung)

**User-Vorgabe:** Migrationsreihenfolge nach Neubewertung durch **Judge** selbstständig festlegen und umsetzen.

**Verbindliche Reihenfolge (Judge bestätigt):**
1. **Ring-0 / VPS-Sync:** core_directives mit `sync_core_directives_to_vps.py` auf VPS bringen (SSH-Tunnel).
2. **Cursor-Reduktion:** Gemäß CURSOR_ATLAS_SPEC (.cursorrules entlasten, 1–4.mdc ohne Tetralogie-Kopie, Holschuld in Schicht-3-Agenten).
3. **VPS-Abgleich:** Prüfung, was OC Brain auf VPS in ChromaDB hat (optional, siehe VERGLEICHSDOKUMENT).
4. **DB-Migration (Code/Query):** Abfragen in chroma_client und API auf gravitationskonformes Verhalten umstellen (kein where_filter; einheitliche Pipeline Alt/Neu); Rollback-Pfad definieren.

**Begründung:** Die Reihenfolge ist sinnvoll: Zuerst die kanonische Wahrheit (Ring-0) auf den VPS bringen, dann die Agenten-Umgebung vereinheitlichen (Cursor-Reduktion), danach den Ist-Zustand auf dem VPS prüfen (VPS-Abgleich), zuletzt die Query-Logik umstellen – so bleibt ein klares Rollback (nur Schritt 4 code-seitig zurücknehmen) und es entstehen keine divergierenden Wahrheiten durch vorzeitige Code-Änderungen.
