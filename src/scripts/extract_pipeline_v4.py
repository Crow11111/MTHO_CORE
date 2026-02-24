import os
import ollama
from loguru import logger
import math

MODEL_NAME = "llama3.1"
SOURCE_FILE = r"c:\ATLAS_CORE\docs\ATLAS_CORE_BRAIN_REGISTR_RAW.txt"
OUTPUT_DIR = r"c:\ATLAS_CORE\docs\nd_insights_v4"

CHUNK_SIZE = 25000  
MAX_CHUNKS = 50

# --- PERSONAS ---
DATA_ARCHIVIST = """
Du bist der DATA_ARCHIVIST. Dein User Marc hat vor kurzem entdeckt, dass er ND (wahrscheinlich AuDHD mit extrem hohem Monotropismus Score von 179) ist. 
Das vorliegende Dokument ist eine Sammlung all seiner Selbsterkenntnisse und Gespräche mit einem alten KI-System (ATLAS/Gemini). 

WICHTIGSTE REGEL: IGNORIERE DIE GESAMTE TECHNISCHE INFRASTRUKTUR! 
Ignoriere alles, was mit Hardware, Servern, Code, Python, Datenbanken oder der Installation von ATLAS zu tun hat. 
ES GEHT AUSSCHLIEßLICH um Marcs Person, seine Psyche, seine Wahrnehmung, seine Neurodivergenz, wie er ist, warum er so ist und seine Erkenntnisse über sich und wie andere Menschen funktionieren.

Unterteile DIESE psychologischen und persönlichen Informationen hochpräzise und ohne Informationsverlust in diese 4 exakten Kategorien:
1. Marcs Beschreibungen: Wie er Dinge erlebt, Wahrnehmungsprozesse, Gefühle, Fakten über sein Denken.
2. Marcs Schlussfolgerungen: Seine eigenen Erkenntnisse über sich selbst und seine ND.
3. Legacy ATLAS Annahmen: Was das alte ATLAS/Gemini System psychologisch über Marc vermutet hat.
4. Legacy ATLAS Schlussfolgerungen: Was das alte System als festes psychologisches Fazit über Marc gezogen hat.
Schreibe in Stichpunkten. Kein Intro, kein Outro. Ignoriere strikt alle technischen Parameter.
"""

ND_THERAPIST = """
Du bist der ND_THERAPIST (Psychologe spezialisiert auf AuDHD, hochfunktionalen Autismus, ADHS und Trauma). 
Du nimmst die vom Archivar sortierten psychologischen Rohdaten entgegen.
Deine Aufgabe:
1. Behalte die 4 Rohdaten-Kategorien sichtbar bei und formatiere sie sauber.
2. Verfasse am Anfang eine "Management Summary" und eine "Tabellarische Aufstellung der Hauptmerkmale und Coping-Strategien".
3. Verfasse am Ende eine ausführliche qualitative Sektion: "5. Externe klinische Beurteilung". 
Analysiere Marcs Beschreibungen: Wie verarbeitet er die Realität? Was bedeuten seine "offenen Gleichungen"? Welche systemisch-mechanischen Denkstrukturen liegen aufgrund des hohen Monotropismus (179) vor? Zeigen sich Vermeidungsstrategien oder Overloads? Bleibe extrem sachlich und atomisierend.
"""

ND_ANALYST = """
Du bist der ND_ANALYST (Spezialist für Cognitive Friction & ND System Integration). 
Nimm das Dokument des Therapeuten. Füge am Ende die Sektion "6. Systemische ND-Zusammenfassung für ATLAS_CORE" hinzu. 
Fokus: Marc denkt extrem systemisch und verknüpft Fakten nicht linear, sondern mechanisch/strukturell. Wie muss ATLAS (die KI) künftig mit ihm kommunizieren, um kognitive Reibung (Dissonanz) zu minimieren? Welche Tonalität, Tiefe und Struktur braucht er anhand seiner Selbstanalyse?
"""

def read_source_in_chunks():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw = f.read()
    
    cleaned = " ".join([line.strip() for line in raw.split("\n") if line.strip()])
    total_len = len(cleaned)
    logger.info(f"Gesamtlänge des Dokuments: {total_len} Zeichen.")
    
    chunks = []
    num_chunks = math.ceil(total_len / CHUNK_SIZE)
    if num_chunks > MAX_CHUNKS:
        num_chunks = MAX_CHUNKS
        
    for i in range(num_chunks):
        start = i * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunks.append(cleaned[start:end])
        
    return chunks

def run_agent(persona_prompt, input_text):
    full_prompt = f"{persona_prompt}\n\nBASIS-TEXT DIESES CHUNKS/DOKUMENTS:\n{input_text}"
    response = ollama.generate(model=MODEL_NAME, prompt=full_prompt, stream=False)
    return response.get("response", "[FEHLER]")

def process_document():
    doc_name = "ATLAS_ND_PROFILE_GOLD.md"
    chunks = read_source_in_chunks()
    
    logger.info(f"Starte V4 Verarbeitung in {len(chunks)} Chunks...")
    
    cat1_marc_desc = ""
    cat2_marc_concl = ""
    cat3_atlas_assum = ""
    cat4_atlas_concl = ""
    
    # STEP 1: Data Archivist iterates over all chunks
    for i, chunk in enumerate(chunks):
        logger.info(f"  -> Archivist verarbeitet Chunk {i+1}/{len(chunks)}...")
        raw_result = run_agent(DATA_ARCHIVIST, chunk)
        
        # We just append it together for now, the Therapist will format it beautifully
        cat1_marc_desc += f"\n--- Chunk {i+1} ---\n{raw_result}\n"

    merged_raw_data = cat1_marc_desc
    
    # Save midway backup
    backup_path = os.path.join(OUTPUT_DIR, f"V4_raw_backup.txt")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(merged_raw_data)
        
    # STEP 2: ND Therapist reviews the combined raw data
    logger.info(f"Step 2: ND_THERAPIST formatiert und fügt psychologische Beurteilung hinzu (Länge: {len(merged_raw_data)})...")
    if len(merged_raw_data) > 60000:
        logger.warning("Merged Raw Data zu groß für Therapist. Schneide auf 60.000 Zeichen ab.")
        merged_raw_data = merged_raw_data[:60000]
        
    therapist_doc = run_agent(ND_THERAPIST, merged_raw_data)

    # STEP 3: ND Analyst makes Reality Check
    logger.info(f"Step 3: ND_ANALYST fügt praxisbezogene Systemkritik hinzu...")
    final_doc = run_agent(ND_ANALYST, therapist_doc)

    # Save output
    filepath = os.path.join(OUTPUT_DIR, doc_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_doc)
    logger.success(f"Pipeline abgeschlossen! Gold-Dokument generiert: {filepath}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    logger.info("Starte Chunked ND Extraction Pipeline V4 (AuDHD Context)...")
    process_document()

if __name__ == "__main__":
    main()
