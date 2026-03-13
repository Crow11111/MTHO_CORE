# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from loguru import logger

from src.network.chroma_client import get_collection, COLLECTION_KNOWLEDGE_GRAPH, is_remote

# Paths & Setup (Insights liegen lokal)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.normpath(os.path.join(_script_dir, "..", ".."))
INSIGHTS_DIR = os.path.join(_project_root, "docs", "nd_insights")
if not os.path.exists(INSIGHTS_DIR):
    INSIGHTS_DIR = r"c:\CORE\docs\nd_insights"


def init_db():
    logger.info("Verbinde zu ChromaDB (lokal oder VPS laut .env)...")
    collection = get_collection(COLLECTION_KNOWLEDGE_GRAPH, create_if_missing=True)
    logger.info(f"Collection {COLLECTION_KNOWLEDGE_GRAPH} bereit (remote={is_remote()}).")
    return collection

def ingest_document(collection, file_name, category):
    file_path = os.path.join(INSIGHTS_DIR, file_name)
    if not os.path.exists(file_path):
        logger.warning(f"Datei nicht gefunden: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We chunk the document by paragraphs to create individual embedding nodes
    chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 50]
    
    docs = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        docs.append(chunk)
        metadatas.append({
            "source_file": file_name,
            "category": category,
            "chunk_index": i
        })
        # Deterministic IDs
        ids.append(f"{file_name}_chunk_{i}")

    if docs:
        logger.info(f"Ingestiere {len(docs)} Knotenpunkte aus {file_name} in die Datenbank...")
        collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
        logger.success(f"{file_name} erfolgreich indiziert.")

def main():
    try:
        collection = init_db()
        # Ingest Factual Data
        ingest_document(collection, "01_ND_FAKTEN_FINAL.md", "FACTUAL_INSIGHT")
        
        # Ingest Assumed Data
        ingest_document(collection, "02_ND_ANNAHMEN_FINAL.md", "ASSUMED_INSIGHT")
        
        logger.success("Alle Daten in die ChromaDB knowledge_graph Collection überführt.")
    except Exception as e:
        logger.error(f"Fehler bei der Datenbank-Ingestion: {e}")

if __name__ == "__main__":
    main()
