"""
ChromaDB-Client für ATLAS_CORE (lokal oder remote auf VPS).
Liest Konfiguration aus .env; bei CHROMA_HOST → HttpClient (VPS), sonst PersistentClient (lokal).
Collections laut Schnittstelle: shell_knowledge_graph, core_brain_registr, krypto_scan_buffer.
"""
import os
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

# Remote (VPS): CHROMA_HOST + CHROMA_PORT (Standard 8000)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
# Lokal (Dreadnought/Windows), wenn CHROMA_HOST leer
CHROMA_LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\CORE\data\chroma_db")

# Collection-Namen laut 03_DATENBANK_VECTOR_STORE_OSMIUM.md + ATLAS Neocortex V1
COLLECTION_SHELL = "shell_knowledge_graph"
COLLECTION_CORE_BRAIN = "core_brain_registr"
COLLECTION_KRYTO_SCAN = "krypto_scan_buffer"
COLLECTION_EVENTS = "events"
COLLECTION_INSIGHTS = "insights"


def get_chroma_client():
    """Liefert ChromaDB-Client: HttpClient bei CHROMA_HOST, sonst PersistentClient lokal."""
    try:
        import chromadb
    except ImportError:
        raise ImportError("chromadb nicht installiert: pip install chromadb")

    if CHROMA_HOST:
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    if not os.path.exists(CHROMA_LOCAL_PATH):
        os.makedirs(CHROMA_LOCAL_PATH)
    return chromadb.PersistentClient(path=CHROMA_LOCAL_PATH)


def get_collection(name: str = COLLECTION_SHELL, create_if_missing: bool = True):
    """Holt die angegebene Collection (Standard: shell_knowledge_graph)."""
    client = get_chroma_client()
    if create_if_missing:
        return client.get_or_create_collection(
            name=name,
            metadata={"description": f"ATLAS_CORE Collection: {name}"},
        )
    return client.get_collection(name=name)


def is_remote() -> bool:
    """True, wenn ChromaDB auf VPS (CHROMA_HOST) genutzt wird."""
    return bool(CHROMA_HOST)


def is_configured() -> bool:
    """True, wenn ChromaDB nutzbar ist (CHROMA_HOST gesetzt oder lokaler Pfad konfigurierbar)."""
    return bool(CHROMA_HOST) or bool(CHROMA_LOCAL_PATH)


# Dimension für events/insights (Metadata-Only-Queries; Embedding optional)
EVENTS_EMBEDDING_DIM = 384


def get_events_collection():
    """Collection 'events' für ATLAS Neocortex (Sensor-Events). add() mit embeddings=[[0]*EVENTS_EMBEDDING_DIM]."""
    return get_collection(COLLECTION_EVENTS, create_if_missing=True)


def add_event_to_chroma(event_id: str, event: dict, metadata_flat: dict) -> bool:
    """Fügt ein Event in ChromaDB events ein. metadata_flat: nur str/int/float/bool."""
    try:
        col = get_events_collection()
        col.add(
            ids=[event_id],
            embeddings=[[0.0] * EVENTS_EMBEDDING_DIM],
            metadatas=[metadata_flat],
            documents=[__import__("json").dumps(event, ensure_ascii=False)],
        )
        return True
    except Exception:
        return False
