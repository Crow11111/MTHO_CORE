import os
import sqlite3
from loguru import logger

INSIGHTS_DIR = r"c:\ATLAS_CORE\docs\nd_insights_full"
DB_DIR = r"c:\ATLAS_CORE\data\argos_db"
DB_FILE = os.path.join(DB_DIR, "argos_knowledge_graph.sqlite")

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the argos_knowledge_graph table based on the specifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS argos_knowledge_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component1 TEXT NOT NULL,
            component2 TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            source_file TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    logger.info(f"Relational Database bereit unter {DB_FILE}")
    return conn

def ingest_document(conn, file_name, relation_type):
    file_path = os.path.join(INSIGHTS_DIR, file_name)
    if not os.path.exists(file_path):
        logger.warning(f"Datei nicht gefunden: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into meaningful insight chunks
    chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 20]
    
    cursor = conn.cursor()
    count = 0
    for chunk in chunks:
        # component1: The subject / persona
        # component2: The actual insight payload
        cursor.execute("""
            INSERT INTO argos_knowledge_graph (component1, component2, relation_type, source_file)
            VALUES (?, ?, ?, ?)
        """, ("Marc_ND_Profile", chunk, relation_type, file_name))
        count += 1
        
    conn.commit()
    logger.success(f"{count} Datensätze aus {file_name} erfolgreich als {relation_type} indiziert.")

def main():
    try:
        conn = init_db()
        # Wipe DB before inserting full dataset to avoid duplicates from previous run
        conn.cursor().execute("DELETE FROM argos_knowledge_graph")
        conn.commit()
        
        ingest_document(conn, "01_ND_FAKTEN_VOLLSTAENDIG.md", "FACTUAL_INSIGHT")
        ingest_document(conn, "02_ND_ANNAHMEN_VOLLSTAENDIG.md", "ASSUMED_INSIGHT")
        conn.close()
        logger.success("Alle Daten erfolgreich in die relationale ARGOS-Wissensdatenbank überführt.")
    except Exception as e:
        logger.error(f"Fehler bei DB Ingestion: {e}")

if __name__ == "__main__":
    main()
