<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Gravitator Spec (GQA Refactor F5)

**Status:** Implementiert (2026-03-06: async + Takt-0-Gate integriert)
**Ziel:** Embedding-basiertes Routing ersetzt statische Collection-Auswahl in GQA (General Query Architecture). Kein `collection=all`; Route ausschließlich via Kosinus-Similarität (θ=0.22). Vor jedem Routing wird asynchron das Takt-0-Gate geprüft.

---

## 1. Kontext

Der **Gravitator** ist das Herzstück des GQA-Refactors. Statt bei jeder Query alle ChromaDB-Collections zu durchsuchen oder eine feste Collection zu wählen, routet er die Anfrage semantisch zu den relevantesten Collections.

### Vorher (statisch)
- `collection=all` → alle Collections abfragen (teuer)
- `collection=simulation_evidence` → nur Evidence (starr)

### Nachher (Gravitator)
- `query_text` → Embedding → Kosinus-Similarität vs. Collection-Repräsentanten → Top-K mit Score > Threshold

---

## 2. Architektur

```
query_text
    │
    ▼
┌─────────────────────┐
│ Embedding (ChromaDB  │  384 dim, all-MiniLM-L6-v2
│ Default)             │  (konsistent mit Collections)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Kosinus-Similarität │  vs. vorberechnete Repräsentanten
│ vs. Repräsentanten  │  (state_to_embedding_text + Collection-Signatur)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Top-K, Score > θ    │  K=3, θ=0.22 (konfigurierbar)
└──────────┬──────────┘
           │
           ▼
    [CollectionTarget, ...]
```

---

## 3. Collection-Typen (Zero-State-Feld-kompatibel)

| Collection | type (Zero-State) | Repräsentant-Signatur |
|------------|-------------|------------------------|
| simulation_evidence | evidence | Simulationstheorie-Indizien, Evidenz, physikalische/informationstheoretische Argumente |
| core_directives | directive | Ring-0/1 Direktiven, System-Prompts, Governance, Compliance |
| session_logs | session | Gesprächs-Sessions, Session-Logs, Dialoge, Turn-Turns |
| shell_knowledge_graph | context | Shell Knowledge Graph, Kontext, Wissensgraphen, Chunk-Daten |
| marc_li_patterns | pattern | Marc-LI Patterns, Muster, ND-Patterns |

---

## 4. Repräsentanten-Generierung

Jeder Collection-Repräsentant kombiniert:

1. **CORE-Bootloader** (`state_to_embedding_text()` aus `atlas_state_vector.py`)
2. **Collection-spezifische Signatur** (Keywords, GTAC/CORE-Bezug)

```python
repr_text = state_to_embedding_text() + "\n" + collection_signature
```

Dadurch ist der Repräsentant sowohl im CORE-Kontext verankert als auch semantisch unterscheidbar.

---

## 5. API

### `route(query_text: str, top_k: int = 3, threshold: float = 0.35) -> list[CollectionTarget]`

**Parameter:**
- `query_text`: Suchanfrage (wird embedded)
- `top_k`: Max. Anzahl Collections (Default: 3)
- `threshold`: Min. Kosinus-Similarität (Default: 0.22)

**Rückgabe:** Liste von `CollectionTarget` (name, score, type), absteigend nach Score.

### `CollectionTarget`

```python
@dataclass
class CollectionTarget:
    name: str       # z.B. "simulation_evidence"
    score: float    # Kosinus-Similarität 0..1
    type: str       # evidence | directive | session | context | pattern
```

---

## 6. Fallback-Logik

**Wenn kein Match** (alle Scores < Threshold):

1. **Fallback-Liste:** `[simulation_evidence, core_directives]`
   - simulation_evidence: breites Wissen, oft relevant
   - core_directives: Governance/Compliance-Fragen

2. **Alternativ:** Alle semantisch durchsuchbaren Collections zurückgeben (wie `collection=all`), aber mit niedrigem Score (0.0) markiert.

**Implementierung:** Fallback liefert `[CollectionTarget(name="simulation_evidence", score=0.0, type="evidence"), ...]` mit `score=0.0` als Indikator für Fallback.

---

## 7. Embedding-Konsistenz

- **Modell:** ChromaDB Default (all-MiniLM-L6-v2, 384 dim)
- **Quelle:** `chromadb.utils.embedding_functions.DefaultEmbeddingFunction()`
- **Begründung:** Collections nutzen ChromaDB Default; gleicher Vektorraum für Query und Repräsentanten.

---

## 8. Integration (GQA)

```python
# Vorher (atlas_knowledge.py)
if collection in ("all", "simulation_evidence"):
    sim = query_simulation_evidence(q, n_results=limit)
    ...

# Nachher (GQA)
targets = gravitator.route(q)
for t in targets:
    if t.name == "simulation_evidence":
        sim = query_simulation_evidence(q, n_results=limit)
        ...
```

---

## 9. Referenzen

- `src/config/core_state.py` (state_to_embedding_text)
- `docs/02_ARCHITECTURE/WUJI_FIELD_SCHEMA.md` (Collection-Typen)
- `src/network/chroma_client.py` (Collection-Namen, async Query-Funktionen)
- `src/logic_core/takt_gate.py` (Takt-0-Check vor Routing)

---

## 10. Threshold-Kalibrierung

Der Default-Threshold (0.22) ist empirisch. Kurze Queries können niedrigere Scores liefern; die Fallback-Logik greift dann. Bei Bedarf: `route(q, threshold=0.15)` für sensitiveres Routing.
