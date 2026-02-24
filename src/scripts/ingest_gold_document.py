import os
import requests
from loguru import logger
import re

INSIGHTS_DIR = r"c:\ATLAS_CORE\docs\nd_insights_v4"
API_BASE_URL = "http://localhost:8000"

def ingest_gold_document(file_name):
    file_path = os.path.join(INSIGHTS_DIR, file_name)
    if not os.path.exists(file_path):
        logger.warning(f"Datei nicht gefunden: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [chunk.strip() for chunk in content.split("\n\n") if len(chunk.strip()) > 30 and not chunk.startswith("---")]
    
    count_kg = 0
    count_cb = 0
    
    for chunk in chunks:
        # Determine relation for Knowledge Graph
        relation_type = "influence"
        if "Marc" in chunk or "Ich" in chunk or "Analyst" in chunk:
            relation_type = "causality"
            
        # 1. Post to Knowledge Graph
        kg_payload = {
            "component1": "Marc_AuDHD_Profile",
            "component2": chunk,
            "relation_type": relation_type,
            "source_file": file_name
        }
        res_kg = requests.post(f"{API_BASE_URL}/knowledge_graph", json=kg_payload)
        if res_kg.status_code == 200:
            count_kg += 1

        # 2. Post to Core Brain Registr (as immutable facts)
        cb_payload = {
            "system_status": "active",
            "content": f"[GOLD_PROFILE] {chunk}"
        }
        res_cb = requests.post(f"{API_BASE_URL}/core_brain", json=cb_payload)
        if res_cb.status_code == 200:
            count_cb += 1
            
    logger.success(f"{count_kg} Relationen und {count_cb} statische Fakten aus {file_name} erfolgreich via API indiziert.")

def main():
    try:
        # Check if API is reachable
        requests.get(f"{API_BASE_URL}/knowledge_graph", timeout=2)
        
        # We don't wipe via API (no delete endpoint yet), so we just append the Gold Profile.
        logger.info("Starte Ingestion über Osmium FastAPI Backend...")
        ingest_gold_document("ATLAS_ND_PROFILE_GOLD.md")
        logger.success("Das Gold-Dokument wurde erfolgreich in die REST-API der ARGOS-Wissensdatenbank überführt.")
    except requests.exceptions.ConnectionError:
        logger.error(f"Konnte nicht zur API unter {API_BASE_URL} verbinden. Läuft db_backend.py?")
    except Exception as e:
        logger.error(f"Fehler bei DB Ingestion: {e}")

if __name__ == "__main__":
    main()
