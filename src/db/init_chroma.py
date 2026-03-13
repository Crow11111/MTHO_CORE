# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import chromadb
from chromadb.config import Settings

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")

def init_chroma():
    client = chromadb.HttpClient(
        host=CHROMA_HOST, 
        port=CHROMA_PORT,
        settings=Settings(allow_reset=True)
    )

    collection_name = "user_state_vectors"
    
    # Spezifikationen:
    # - embeddings: 1536-dim (multimodale Repräsentation).
    # - metadata: { timestamp: int, entropy_level: float, context_tags: list[str], resolution_id: uuid }
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"Collection '{collection_name}' initialized.")

if __name__ == "__main__":
    init_chroma()
