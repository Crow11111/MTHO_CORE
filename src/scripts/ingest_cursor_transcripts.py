import os
import sys
import json
import uuid
import glob
import asyncio
from datetime import datetime

# Windows cp1252-Schutz für stdout (PowerShell Encoding-Protokoll)
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")

# Root-Pfad zum Importieren der CORE Module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.network.chroma_client import get_session_logs_collection

# Konfiguration
TRANSCRIPTS_DIR = r"C:\Users\MtH\.cursor\projects\c-CORE-CORE\agent-transcripts"
BATCH_SIZE = 10  # Kleine Batches, um API Rate-Limits (z.B. Gemini/Ollama) zu schonen
DELAY_BETWEEN_BATCHES = 2.0  # Wartezeit in Sekunden
MAX_TEXT_LENGTH = 4000  # Abschneiden von zu langen Code-Blöcken für Embeddings

async def extract_turns(filepath: str) -> list:
    """Extrahiert Benutzer- und Assistenten-Interaktionen aus einer JSONL-Datei."""
    turns = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    role = data.get("role", "unknown")
                    message = data.get("message", {})
                    content = message.get("content", [])
                    
                    # Nur Texte extrahieren (keine Bilder/Tool-Outputs)
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                            
                    full_text = "\n".join(text_parts).strip()
                    
                    if full_text:
                        # Überlange Texte abschneiden, um Embedding-Token-Limits zu respektieren
                        if len(full_text) > MAX_TEXT_LENGTH:
                            full_text = full_text[:MAX_TEXT_LENGTH] + "\n... [TRUNCATED DUE TO LENGTH]"
                            
                        turns.append({
                            "role": role,
                            "text": full_text,
                            "line_idx": line_idx
                        })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"[ERROR] Fehler beim Lesen von {filepath}: {e}")
        
    return turns

async def process_transcripts():
    print(f"[CORE] Starte Ingest-Analyse im Verzeichnis:\n  {TRANSCRIPTS_DIR}")
    
    jsonl_files = glob.glob(os.path.join(TRANSCRIPTS_DIR, "**", "*.jsonl"), recursive=True)
    print(f"[INFO] {len(jsonl_files)} JSONL-Dateien gefunden.")
    
    if not jsonl_files:
        print("[WARN] Keine Transcripts gefunden. Abbruch.")
        return

    print("[INFO] Verbinde mit ChromaDB (Collection: session_logs)...")
    col = await get_session_logs_collection()
    
    total_ingested = 0
    
    for filepath in jsonl_files:
        filename = os.path.basename(filepath)
        session_id = filename.replace(".jsonl", "")
        
        # Versuche das Erstelldatum der Datei als Session-Datum zu nehmen
        try:
            mtime = os.path.getmtime(filepath)
            session_date = datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            session_date = datetime.now().isoformat()
            
        print(f"  -> Lese: {filename}")
        turns = await extract_turns(filepath)
        
        if not turns:
            continue
            
        ids = []
        documents = []
        metadatas = []
        
        for turn in turns:
            # Erzeuge eindeutige ID pro Turn
            turn_id = f"{session_id}_L{turn['line_idx']}_{uuid.uuid4().hex[:6]}"
            
            ids.append(turn_id)
            documents.append(turn["text"])
            metadatas.append({
                "source": "cursor_agent_transcript",
                "session_id": session_id,
                "session_date": session_date,
                "speaker": turn["role"],
                "turn_number": turn["line_idx"],
                "topics": "cursor_history"
            })
            
            # Batch voll? Dann in ChromaDB schieben
            if len(ids) >= BATCH_SIZE:
                try:
                    await asyncio.to_thread(
                        col.add,
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas
                    )
                    total_ingested += len(ids)
                    print(f"    [OK] Batch von {len(ids)} Turns eingefügt. Warte {DELAY_BETWEEN_BATCHES}s...")
                    await asyncio.sleep(DELAY_BETWEEN_BATCHES)
                except Exception as e:
                    print(f"    [FEHLER] Batch konnte nicht geladen werden: {e}")
                finally:
                    ids, documents, metadatas = [], [], []
                    
        # Reste pushen
        if ids:
            try:
                await asyncio.to_thread(
                    col.add,
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                total_ingested += len(ids)
                print(f"    [OK] Finaler Batch von {len(ids)} Turns eingefügt. Warte {DELAY_BETWEEN_BATCHES}s...")
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)
            except Exception as e:
                print(f"    [FEHLER] Finaler Batch konnte nicht geladen werden: {e}")

    print(f"\n[ERFOLG] Ingest abgeschlossen. {total_ingested} Interaktionen in 'session_logs' geladen.")

if __name__ == "__main__":
    print("=" * 60)
    print("CORE - CURSOR TRANSCRIPTS INGEST (DRY-RUN LOCK)")
    print("=" * 60)
    print("WARNUNG: Dieses Skript parst potenziell Gigabytes an Text.")
    print("Bitte überprüfen, ob das VPS/ChromaDB Limit und die API-Quotas (Embeddings) ausreichen.")
    print("Um den Ingest zu starten, entferne den Kommentar vor 'asyncio.run(process_transcripts())'.")
    print("=" * 60)
    
    # [SICHERHEITS-LOCK]
    # asyncio.run(process_transcripts())
    print("[STATUS] Skript bereit, Ausführung aber durch Sicherheits-Lock blockiert.")
