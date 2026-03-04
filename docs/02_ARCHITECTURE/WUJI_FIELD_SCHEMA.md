# Wuji-Feld Schema (GQA Refactor F8)

**Status:** Migrationskonzept für einheitliche ChromaDB-Collection.  
**Ziel:** Dynamische Filterung statt starrer Collection-Trennung.

---

## 1. Ausgangslage (vps_chroma_full_export.json)

| Collection | IDs | Metadaten |
|------------|-----|-----------|
| simulation_evidence | 58 | category, strength, branch_count, source, date_added, qbase, qbase_complement, qbase_confidence, qbase_scores |
| core_directives | 9 | category, ring_level, priority, date, type, source |
| session_logs | variabel | source, session_date, turn_number, speaker, topics, ring_level |
| argos_knowledge_graph | variabel | source_file, category, chunk_index |
| marc_li_patterns | (leer) | – |

---

## 2. Einheitliches Schema: `wuji_field`

### 2.1 Pflicht-Metadaten (alle Dokumente)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `type` | str | Kategorisierung: `evidence`, `directive`, `session`, `context`, `insight`, `pattern`, `axiom` |
| `source_collection` | str | Herkunft (Migration): `simulation_evidence`, `core_directives`, `session_logs`, `argos_knowledge_graph`, `marc_li_patterns` |
| `date_added` | str | ISO-Datum (YYYY-MM-DD) |

### 2.2 LPIS-Encoding (quaternaere Codierung)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `lpis_base` | str | L \| P \| I \| S (aus atlas_state_vector.LPIS_BASES) |
| `lpis_complement` | str | Paarung laut LPIS_PAIRINGS (L↔I, S↔P) |
| `lpis_confidence` | float | 0.0–1.0, optional |
| `lpis_scores` | str | Format: `"L:0.5|P:0.2|I:0.2|S:0.1"` (optional) |

**Mapping:** `category` → `lpis_base`:
- logisch / logisch-mathematisch → L
- physikalisch → P
- informationstheoretisch / informationell → I
- strukturell / systemisch-emergent → S

### 2.3 Typ-spezifische Metadaten (optional)

| type | Zusätzliche Felder |
|------|--------------------|
| evidence | strength, branch_count, source |
| directive | ring_level, category, priority |
| session | session_date, turn_number, speaker, topics, ring_level |
| context | source_file, chunk_index |
| insight | confidence_score, source_event_ids (JSON-String) |
| pattern | – |
| axiom | category |

### 2.4 ID-Konvention

| source_collection | ID-Prefix | Beispiel |
|-------------------|-----------|----------|
| simulation_evidence | (unverändert) | sim_info_schwarzes_loch |
| core_directives | cd_ | cd_ring0_bias_depth_check |
| session_logs | sl_ | sl_2026-03-01_001 |
| argos_knowledge_graph | arg_ | arg_kg_001 |
| marc_li_patterns | mlp_ | mlp_001 |

---

## 3. ChromaDB-Constraints

- **Metadaten:** Nur `str`, `int`, `float`, `bool`
- **Listen:** Als JSON-String serialisieren (z.B. `context_tags`)
- **Embedding:** ChromaDB Default (384 dim, all-MiniLM-L6-v2)
- **Collection:** `wuji_field` mit `hnsw:space: cosine`

---

## 4. Query-Pattern (dynamische Filterung)

```python
# Nur Evidence
col.query(where={"type": "evidence"}, ...)

# Evidence + LPIS L oder I
col.query(where={"$and": [{"type": "evidence"}, {"lpis_base": {"$in": ["L", "I"]}}]}, ...)

# Ring-0 Direktiven
col.query(where={"$and": [{"type": "directive"}, {"ring_level": 0}]}, ...)

# Session-Turns eines Datums
col.query(where={"$and": [{"type": "session"}, {"session_date": "2026-03-01"}]}, ...)
```

---

## 5. Migrations-Phasen

| Phase | Aktion |
|-------|--------|
| 1 | `wuji_field` Collection erstellen |
| 2 | simulation_evidence → wuji_field migrieren (type=evidence) |
| 3 | core_directives → wuji_field migrieren (type=directive) |
| 4 | session_logs → wuji_field migrieren (type=session) |
| 5 | argos_knowledge_graph → wuji_field migrieren (type=context), falls ChromaDB-Daten vorhanden |
| 6 | chroma_client.py: Query-Funktionen auf wuji_field + where-Filter umstellen |
| 7 | Alte Collections archivieren (nicht löschen) oder als Read-Only belassen |

---

## 6. Rollback-Strategie

- Alte Collections bleiben bis Validierung erhalten
- Migration läuft in Transaktionen (Batch-Upsert)
- Bei Fehler: wuji_field leeren, Retry mit korrigiertem Script

---

## 7. Referenzen

- `src/config/atlas_state_vector.py` (LPIS_BASES, LPIS_PAIRINGS)
- `src/config/engine_patterns.py` (QBASES, QBASE_PAIRS)
- `src/logic_core/quaternary_codec.py` (category → lpis_base Mapping)
- `docs/05_AUDIT_PLANNING/vps_chroma_full_export.json` (Quelldaten)
