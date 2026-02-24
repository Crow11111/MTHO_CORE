import os
import requests
from loguru import logger
import re

INSIGHTS_DIR = r"c:\ATLAS_CORE\docs\nd_insights_v4"
RAW_FILE = os.path.join(INSIGHTS_DIR, "V4_raw_backup.txt")
API_BASE_URL = "http://localhost:8000"

def ingest_deep_archive():
    if not os.path.exists(RAW_FILE):
        logger.error(f"Raw archive file not found: {RAW_FILE}")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split the raw text into paragraphs
    raw_chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 20]
    
    count_kg = 0
    count_skipped = 0

    logger.info(f"Parsing {len(raw_chunks)} raw chunks from deep archive...")

    for chunk in raw_chunks:
        # Basic filtering to avoid pure noise headers
        if chunk.startswith("===") or chunk.startswith("---"):
            count_skipped += 1
            continue

        # Determine relation
        relation_type = "influence"
        if "Marc" in chunk or "System" in chunk:
            relation_type = "causality"
            
        kg_payload = {
            "component1": "Raw_Insight_Node",
            "component2": chunk,
            "relation_type": relation_type,
            "source_file": "V4_raw_backup.txt"
        }
        res_kg = requests.post(f"{API_BASE_URL}/knowledge_graph", json=kg_payload)
        if res_kg.status_code == 200:
            count_kg += 1
        else:
            count_skipped += 1

    logger.success(f"{count_kg} raw insights deeply ingested into argos_knowledge_graph. (Skipped: {count_skipped})")

if __name__ == "__main__":
    try:
        # Check API
        requests.get(f"{API_BASE_URL}/knowledge_graph", timeout=2)
        logger.info("Starting Data Archivist Deep Ingestion...")
        ingest_deep_archive()
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to API at {API_BASE_URL}. Is db_backend.py running?")
    except Exception as e:
        logger.error(f"Database Ingestion Error: {e}")
