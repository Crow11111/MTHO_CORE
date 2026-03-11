---
name: expertise-database
description: Fachgebiet Datenbank-Design und -Betrieb für Schicht-3-Produzenten. ChromaDB, PostgreSQL, SQLite. Schema-Design, Indexing, Migration, Embedding-Strategien. MTHO Collections.
---

# Expertise: Datenbank

## Technologie-Stack

| System | Rolle |
|--------|-------|
| ChromaDB | Vektor-DB, RAG, semantische Suche |
| PostgreSQL | Persistenz, strukturierte Daten |
| SQLite | mtho_knowledge_graph (lokal) |

## Schema-Design-Patterns

- **Normalisierung vs. Denormalisierung**: Abwägung Lese-/Schreiblast
- **Indexing**: B-Tree für Lookups, HNSW/IVF für Vektoren
- **Migration**: Versionierte Skripte, Rollback-Strategie
- **Embedding-Strategien**: Ein Modell pro Collection, Chunk-Größe konsistent

## MTHO Collections (ChromaDB)

| Collection | Zweck |
|------------|-------|
| mtho_knowledge_graph | KG-Relationen, ND-Insights, RAG |
| core_brain_registr | Immutable Systemdaten, Confidence ≥ 0.99 |
| session_logs | Gesprächs-Sessions, semantische Suche |
| events | Mtho-Events, Event-Log |
| core_directives | Direktiven für RAG |
| krypto_scan_buffer | Scan-Puffer |

## Wichtige Patterns

- core_brain_registr: Nur schreiben bei hoher Confidence (Bias Damper)
- mtho_knowledge_graph: component1, component2, relation_type, source_file
- session_logs: add_session_turn, query_session_logs für Kontext
