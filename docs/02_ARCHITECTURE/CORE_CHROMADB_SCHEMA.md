<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE ChromaDB Schema

**Status:** Verbindliche Schema-Definition für alle ChromaDB Collections.  
**VPS:** CHROMA_HOST=187.77.68.250, CHROMA_PORT=8000 (via SSH-Tunnel: `ssh -L 8000:127.0.0.1:8000 root@187.77.68.250`).

---

## Übersicht

| Collection | Embedding | Zweck |
|------------|-----------|-------|
| simulation_evidence | Default (384) | Simulationstheorie-Indizien, RAG |
| session_logs | Default (384) | Gesprächs-Sessions, semantische Suche |
| core_directives | Default (384) | Ring-0/1 Direktiven |
| events | 384 (explizit) | Sensor-Events, Neocortex |
| insights | 384 (explizit) | Destillierte Erkenntnisse, Kausal-Ketten |
| user_state_vectors | 1536 | User-State, Entropie-Kontext |
| shell_knowledge_graph | Default (384) | KG-Relationen, ND-Insights |
| atlas_identity | Default (384) | Wer/Was/Warum ist CORE |
| entities | Default (384) | Personen, Geräte, Systeme |
| relationships | Default (384) | Wer gehört zu wem |

**ChromaDB-Metadaten:** Nur `str`, `int`, `float`, `bool`. Listen als JSON-String speichern.

---

## Existierende Collections (bereits auf VPS)

### simulation_evidence
- **Metadata:** category, strength, branch_count, source, date_added, qbase (L/P/I/S)
- **Embedding:** ChromaDB Default (all-MiniLM-L6-v2, 384 dim)
- **Quelle:** chroma_client.add_simulation_evidence

### session_logs
- **Metadata:** source, session_date, turn_number, speaker, topics, ring_level
- **Embedding:** ChromaDB Default
- **Quelle:** chroma_client.add_session_turn

### core_directives
- **Metadata:** category, ring_level
- **Embedding:** ChromaDB Default
- **Quelle:** chroma_client.add_core_directive

---

## Fehlende Collections (zu erstellen)

### events
- **Embedding:** 384 dim (explizit, metadata-heavy; document = JSON)
- **Metadata:** timestamp, source_device, event_type, priority, processed_by, analysis_pending
- **Quelle:** ATLAS_NEOCORTEX_V1.md, chroma_client.add_event_to_chroma

### insights
- **Embedding:** 384 dim (explizit)
- **Metadata:** confidence_score, source_event_ids (JSON-String), user_feedback
- **Quelle:** ATLAS_NEOCORTEX_V1.md

### user_state_vectors
- **Embedding:** 1536 dim (multimodale Repräsentation)
- **Metadata:** timestamp (int), entropy_level (float), context_tags (JSON-String), resolution_id (str)
- **Quelle:** backups/.../init_chroma.py

### shell_knowledge_graph
- **Embedding:** ChromaDB Default
- **Metadata:** source_file, category, chunk_index; optional: component1, component2, relation_type
- **Quelle:** ingest_nd_insights_to_chroma.py, 03_DATENBANK_VECTOR_STORE.md

---

## Zusätzliche Collections

### atlas_identity
- **Document:** Identity-Text (Wer/Was/Warum ist CORE)
- **Metadata:** version, ring_level
- **Embedding:** ChromaDB Default

### entities
- **Document:** Entity-Beschreibung (Person, Gerät, System)
- **Metadata:** entity_type, domain, source
- **Embedding:** ChromaDB Default

### relationships
- **Document:** Beziehungsbeschreibung (optional)
- **Metadata:** from_entity, to_entity, relation_type
- **Embedding:** ChromaDB Default

---

## Embedding-Dimensionen

| Dimension | Verwendung |
|-----------|------------|
| 384 | ChromaDB Default (all-MiniLM-L6-v2), events, insights |
| 1536 | user_state_vectors (OpenAI-kompatibel, multimodal) |
