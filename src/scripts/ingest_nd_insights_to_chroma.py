import os
import chromadb
from loguru import logger

# Paths & Setup
INSIGHTS_DIR = r"c:\ATLAS_CORE\docs\nd_insights"
DB_PATH = r"c:\ATLAS_CORE\data\chroma_db"

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    logger.info(f"Verbinde zu ChromaDB auf Dreadnought (Pfad: {DB_PATH})...")
    
    # Init persistent client on Dreadnought (Windows Host)
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Get or create the argos_knowledge_graph collection
    collection = client.get_or_create_collection(
        name="argos_knowledge_graph",
        metadata={"description": "ATLAS_CORE Relational Knowledge Database for ND Insights"}
    )
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
        
        logger.success("Alle Daten in die ChromaDB argos_knowledge_graph Collection überführt.")
    except Exception as e:
        logger.error(f"Fehler bei der Datenbank-Ingestion: {e}")

if __name__ == "__main__":
    main()
