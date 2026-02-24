import os
import ollama
from loguru import logger
import math

MODEL_NAME = "llama3.1"
SOURCE_FILE = r"c:\ATLAS_CORE\docs\ATLAS_CORE_BRAIN_REGISTR_RAW.txt"
OUTPUT_DIR = r"c:\ATLAS_CORE\docs\nd_insights_full"

CHUNK_SIZE = 25000  # Approx 25k chars per chunk to safely fit 8B model memory
MAX_CHUNKS = 50     # Failsafe limit

# --- PERSONAS ---
DATA_ARCHIVIST = "Du bist der DATA_ARCHIVIST (Database Master & Lector). Extrahiere kristallklare, differenzierte Datenpunkte aus unstrukturierten Texten. Reduziere nichts auf Kosten von Details. Formuliere objektiv. Antworte in Stichpunkten ohne Intro/Outro."
ND_THERAPIST = "Du bist der ND_THERAPIST (Psychologe spezialisiert auf Neurodivergenz & Trauma). Nimm die gesammelten extrahierten Rohdaten entgegen. Analysiere Coping-Mechanismen und Denkstrukturen. Füge dem Dokument ZWINGEND am Ende eine '# Beurteilung und Einschätzung des ND_THERAPISTS' sowie am Anfang eine '# Management Summary' und eine '# Tabellarische Aufstellung' hinzu."
ND_ANALYST = "Du bist der ND_ANALYST (Spezialist für Cognitive Friction & ND Reality Check). Nimm das therapeutisch bewertete Dokument und hänge ganz am Ende eine Sektion '# ND_ANALYST: Reality Check' an, in der du auf Dissonanzen hinweist oder bestätigst."

def read_source_in_chunks():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    
    cleaned = " ".join([line.strip() for line in raw.split("\n") if line.strip()])
    total_len = len(cleaned)
    logger.info(f"Gesamtlänge des Dokuments: {total_len} Zeichen.")
    
    chunks = []
    num_chunks = math.ceil(total_len / CHUNK_SIZE)
    # Failsafe for extremely long docs to prevent looping forever
    if num_chunks > MAX_CHUNKS:
        logger.warning(f"Dokument zu lang ({num_chunks} Chunks). Limitiere auf die ersten {MAX_CHUNKS} Chunks.")
        num_chunks = MAX_CHUNKS
        
    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunks.append(cleaned[start:end])
        
    return chunks

def run_agent(persona_prompt, user_prompt, input_text=""):
    full_prompt = f"{persona_prompt}\n\nAUFGABE:\n{user_prompt}\n\nBASIS-TEXT:\n{input_text}"
    response = ollama.generate(model=MODEL_NAME, prompt=full_prompt, stream=False)
    return response.get("response", "[FEHLER]")

def process_document(doc_name, archivist_focus):
    chunks = read_source_in_chunks()
    
    logger.info(f"[{doc_name}] Starte Verarbeitung in {len(chunks)} Chunks...")
    merged_raw_data = ""
    
    # STEP 1: Data Archivist iterates over all chunks
    for i, chunk in enumerate(chunks):
        logger.info(f"  -> Archivist verarbeitet Chunk {i+1}/{len(chunks)}...")
        archivist_task = f"Extrahiere strikt nach folgendem Fokus:\n{archivist_focus}"
        result = run_agent(DATA_ARCHIVIST, archivist_task, chunk)
        merged_raw_data += f"\n\n--- CHUNK {i+1} ---\n" + result

    # Save midway backup
    backup_path = os.path.join(OUTPUT_DIR, f"{doc_name}_raw_backup.txt")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(merged_raw_data)
        
    # STEP 2: ND Therapist reviews the combined raw data
    logger.info(f"[{doc_name}] Step 2: ND_THERAPIST formatiert und beurteilt das Gesamtdokument (Länge: {len(merged_raw_data)})...")
    therapist_task = "Strukturiere das gesamte Dokument um: 1. Management Summary, 2. Tabellarische Aufstellung, 3. Die Rohdaten strukturieren, 4. Deine tiefgreifende Beurteilung und Einschätzung."
    # Pass only the first 60k of merged raw to prevent therapist context overflow
    if len(merged_raw_data) > 60000:
        logger.warning("Merged Raw Data zu groß für Therapist. Schneide auf 60.000 Zeichen ab.")
        merged_raw_data = merged_raw_data[:60000]
        
    therapist_doc = run_agent(ND_THERAPIST, therapist_task, merged_raw_data)

    # STEP 3: ND Analyst makes Reality Check
    logger.info(f"[{doc_name}] Step 3: ND_ANALYST macht den Reality Check...")
    analyst_task = "Lies das erstellte Dokument. Hänge unten DEIN URTEIL als ND_ANALYST an. Beurteile das System aus ND-Sicht."
    final_doc = run_agent(ND_ANALYST, analyst_task, therapist_doc)

    # Add back the full raw data for preservation at the very end
    final_output = final_doc + "\n\n# APPENDIX: UNGEKÜRZTE ROHDATEN DES DATA ARCHIVIST\n\n" + merged_raw_data

    # Save output
    filepath = os.path.join(OUTPUT_DIR, doc_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_output)
    logger.success(f"[{doc_name}] Pipeline abgeschlossen! Gespeichert unter {filepath}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    logger.info("Starte Chunked ND Extraction Pipeline (Full Document)...")
    
    # Document 1: Factual Insights
    process_document(
        "01_ND_FAKTEN_VOLLSTAENDIG.md",
        "Extrahiere NUR GESICHERTE FAKTEN aus dem Text. (Fähigkeiten, explizit genannte Ereignisse, berufliche Stationen, explizit dokumentierte Reaktionen). Lasse Interpretationen weg."
    )
    
    # Document 2: Assumed Insights
    process_document(
        "02_ND_ANNAHMEN_VOLLSTAENDIG.md",
        "Extrahiere NUR ANNAHMEN, HYPOTHESEN und PSYCHOLOGISCHE EINSCHÄTZUNGEN. Was wurde nur zwischen den Zeilen angedeutet? Wo vermutet das System Trauma, Überlastung oder Dissonanz?"
    )

if __name__ == "__main__":
    main()
