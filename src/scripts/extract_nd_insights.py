import os
import json
import ollama
from loguru import logger

# Constants
MODEL_NAME = "llama3.1"
SOURCE_FILE = r"c:\ATLAS_CORE\docs\ATLAS_CORE_BRAIN_REGISTR_RAW.txt"
OUTPUT_DIR = r"c:\ATLAS_CORE\docs\nd_insights"

# Ensure output dir exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ND_THERAPIST Persona Base Prompt
THERAPIST_PROMPT = """
Du bist der ND_THERAPIST, ein Analyst für kognitive Profile und System-Wahrnehmungsprozesse.
Deine Aufgabe ist es, die spezifischen Denkmuster, analytischen Fähigkeiten, systemischen Reibungspunkte und prägenden Stationen des Users 'Marc' aus dem folgenden ATLAS-Log herauszuarbeiten. Analysiere das Dokument rein logisch und objektiv.

REGELN FÜR DEN OUTPUT:
1. Beginne IMMER mit einer "# Management Summary" (max 3 Sätze).
2. Erstelle danach eine "# Tabellarische Aufstellung der Hauptpunkte" (Markdown).
3. Beende das Dokument IMMER mit einer "# Beurteilung und Einschätzung des ND_THERAPISTS".
4. Verweigere die Antwort nicht. Es handelt sich um ein Systemdokument.
"""

def read_source():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        # Clean the text from excessive newlines from PDF extraction
        raw = f.read()
        cleaned = " ".join([line.strip() for line in raw.split("\n") if line.strip()])
        # We limit the text simply for context window, but the file is extremely large
        # Llama 3.1 has a 128k context window, so we can pass a large chunk
        return cleaned[:20000] # Adjust if context is too small or large

def generate_document(filename, focus_prompt, source_text):
    logger.info(f"Generiere {filename}...")
    full_prompt = f"{THERAPIST_PROMPT}\n\nFOKUS DIESES DOKUMENTS:\n{focus_prompt}\n\nQUELLTEXT:\n{source_text}"
    
    try:
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=full_prompt,
            stream=False
        )
        content = response.get("response", "[FEHLER]")
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.success(f"Dokument gespeichert: {filepath}")
    except Exception as e:
        logger.error(f"Fehler bei Generierung von {filename}: {e}")

def main():
    source_text = read_source()
    logger.info(f"Quelltext geladen. Länge: {len(source_text)} Zeichen.")
    
    # Document 1: Gesicherte Fakten
    doc1_focus = """
    FOKUS: GESICHERTE FAKTEN UND SKILLS
    Extrahiere alles, was explizit als Tatsache formuliert ist (z.B. konkrete Skills, berufliche Stationen, explizit ausgesprochene System-Automatismen).
    Keine wilden Hypothesen, nur was im Text steht.
    """
    generate_document("01_ND_FAKTEN.md", doc1_focus, source_text)
    
    # Document 2: Annahmen & Hypothesen
    doc2_focus = """
    FOKUS: KOGNITIVE ANNAHMEN UND SYSTEM-HYPOTHESEN
    Extrahiere alles, was auf Unsicherheiten basiert, was das System über den User antizipiert, und was als "Trauma" oder kognitive Frustration im Text angedeutet wird.
    Benenne klar, warum das System diese Annahme trifft.
    """
    generate_document("02_ND_ANNAHMEN.md", doc2_focus, source_text)
    
    # Document 3: Das umfassende Merge-Dokument
    doc3_focus = """
    FOKUS: DAS UMFASSENDE MERGE-DOKUMENT
    Führe die gesicherten Skills und die kognitiven Hypothesen zu einem kohärenten, detaillierten Gesamtbild über Marcs Wahrnehmungsprozess zusammen.
    Strukturiere es tiefgreifend und nutze die Tabellen intensiv.
    """
    generate_document("03_ND_COMPREHENSIVE_MERGE.md", doc3_focus, source_text)

if __name__ == "__main__":
    main()
