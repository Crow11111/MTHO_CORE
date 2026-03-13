# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Erstellt fehlende ChromaDB Collections auf VPS oder lokal.
Nutzt get_chroma_client() aus chroma_client; CHROMA_HOST aus .env.
Collections laut docs/02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.network.chroma_client import (
    get_chroma_client,
    EVENTS_EMBEDDING_DIM,
    COLLECTION_EVENTS,
    COLLECTION_INSIGHTS,
    COLLECTION_KNOWLEDGE_GRAPH,
    is_remote,
)

# Fehlende + zusätzliche Collections
COLLECTION_USER_STATE_VECTORS = "user_state_vectors"
COLLECTION_CORE_IDENTITY = "core_identity"
COLLECTION_ENTITIES = "entities"
COLLECTION_RELATIONSHIPS = "relationships"

USER_STATE_DIM = 1536


def create_collections():
    """Legt alle fehlenden Collections an. Dimension wird bei user_state_vectors per Placeholder gesetzt."""
    client = get_chroma_client()
    created = []
    skipped = []

    # Default-Embedding Collections (ChromaDB 384)
    default_collections = [
        COLLECTION_EVENTS,
        COLLECTION_INSIGHTS,
        COLLECTION_KNOWLEDGE_GRAPH,
        COLLECTION_CORE_IDENTITY,
        COLLECTION_ENTITIES,
        COLLECTION_RELATIONSHIPS,
    ]

    for name in default_collections:
        try:
            col = client.get_or_create_collection(
                name=name,
                metadata={"description": f"CORE: {name}"},
            )
            count = col.count()
            if count == 0:
                created.append(name)
            else:
                skipped.append(f"{name} (existiert, {count} docs)")
        except Exception as e:
            print(f"[FEHLER] {name}: {e}")

    # user_state_vectors: 1536 dim – Placeholder setzt Dimension
    try:
        col = client.get_or_create_collection(
            name=COLLECTION_USER_STATE_VECTORS,
            metadata={"description": "CORE: user_state_vectors (1536 dim)"},
        )
        count = col.count()
        if count == 0:
            col.add(
                ids=["__dim_init__"],
                embeddings=[[0.0] * USER_STATE_DIM],
                documents=[""],
                metadatas=[{"timestamp": 0, "entropy_level": 0.0}],
            )
            col.delete(ids=["__dim_init__"])
            created.append(COLLECTION_USER_STATE_VECTORS)
        else:
            skipped.append(f"{COLLECTION_USER_STATE_VECTORS} (existiert, {count} docs)")
    except Exception as e:
        print(f"[FEHLER] {COLLECTION_USER_STATE_VECTORS}: {e}")

    return created, skipped


def main():
    print("ChromaDB Collections anlegen...")
    print(f"  Ziel: {'VPS (CHROMA_HOST)' if is_remote() else 'lokal (CHROMA_LOCAL_PATH)'}")
    created, skipped = create_collections()
    if created:
        print(f"  Erstellt: {', '.join(created)}")
    if skipped:
        for s in skipped:
            print(f"  Übersprungen: {s}")
    if not created and not skipped:
        print("  Keine Aktion nötig.")
    print("Fertig.")


if __name__ == "__main__":
    main()
