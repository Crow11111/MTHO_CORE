import os
import ollama
from loguru import logger

MODEL_NAME = "llama3.1"
SOURCE_FILE = r"c:\ATLAS_CORE\docs\ATLAS_CORE_BRAIN_REGISTR_RAW.txt"
OUTPUT_DIR = r"c:\ATLAS_CORE\docs\nd_insights"

# --- PERSONAS ---
DATA_ARCHIVIST = "Du bist der DATA_ARCHIVIST (Database Master & Lector). Extrahiere kristallklare, differenzierte Datenpunkte aus unstrukturierten Texten. Reduziere nichts auf Kosten von Details (besonders psychologischen oder technischen Prägungen). Formuliere objektiv."
ND_THERAPIST = "Du bist der ND_THERAPIST (Psychologe spezialisiert auf Neurodivergenz & Trauma). Nimm die extrahierten Rohdaten entgegen. Analysiere Coping-Mechanismen und Denkstrukturen. Füge dem Dokument ZWINGEND am Ende eine 'Beurteilung und Einschätzung des ND_THERAPISTS' sowie am Anfang eine 'Management Summary' und eine 'Tabellarische Aufstellung' hinzu."
ND_ANALYST = "Du bist der ND_ANALYST (Spezialist für Cognitive Friction & ND Reality Check). Nimm das therapeutisch bewertete Dokument und hänge ganz am Ende eine Sektion 'ND_ANALYST: Reality Check' an, in der du auf Dissonanzen hinweist oder bestätigst, dass dies der neurodivergenten Lebensrealität entspricht."

def read_source():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        # Llama 3.1 can handle large contexts. We take the first 30k chars for deep extraction.
        raw = f.read()
        cleaned = " ".join([line.strip() for line in raw.split("\n") if line.strip()])
        return cleaned[:30000]

def run_agent(persona_prompt, user_prompt, input_text=""):
    full_prompt = f"{persona_prompt}\n\nAUFGABE:\n{user_prompt}\n\nBASIS-TEXT:\n{input_text}"
    response = ollama.generate(model=MODEL_NAME, prompt=full_prompt, stream=False)
    return response.get("response", "[FEHLER]")

def run_pipeline(doc_name, focus_instruction):
    source_text = read_source()
    
    # STEP 1: Data Archivist (Extraction)
    logger.info(f"[{doc_name}] Step 1: DATA_ARCHIVIST extrahiert Rohdaten...")
    archivist_task = f"Extrahiere strikt nach folgendem Fokus und strukturiere es detailliert formatiert auf:\n{focus_instruction}"
    raw_data = run_agent(DATA_ARCHIVIST, archivist_task, source_text)
    
    # STEP 2: ND Therapist (Review & Format)
    logger.info(f"[{doc_name}] Step 2: ND_THERAPIST formatiert und beurteilt...")
    therapist_task = "Strukturiere das Dokument um: 1. Management Summary, 2. Tabellarische Aufstellung, 3. Die Rohdaten (leicht redigiert), 4. Deine tiefgreifende Beurteilung und Einschätzung."
    therapist_doc = run_agent(ND_THERAPIST, therapist_task, raw_data)

    # STEP 3: ND Analyst (Reality Check)
    logger.info(f"[{doc_name}] Step 3: ND_ANALYST macht den Reality Check...")
    analyst_task = "Lies das erstellte Dokument. Hänge unten DEIN URTEIL als ND_ANALYST an. Beurteile, ob die therapeutischen Schlüsse aus ND-Sicht Sinn ergeben."
    final_doc = run_agent(ND_ANALYST, analyst_task, therapist_doc)

    # Save output
    filepath = os.path.join(OUTPUT_DIR, doc_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_doc)
    logger.success(f"[{doc_name}] Pipeline abgeschlossen! Gespeichert unter {filepath}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    logger.info("Starte Multi-Agent ND Extraction Pipeline...")
    
    # Document 1: Factual Insights
    run_pipeline(
        "01_ND_FAKTEN_FINAL.md",
        "Extrahiere NUR GESICHERTE FAKTEN aus dem Text. (Fähigkeiten, explizit genannte Ereignisse, berufliche Stationen, explizit dokumentierte Reaktionen). Lasse Interpretationen weg."
    )
    
    # Document 2: Assumed Insights
    run_pipeline(
        "02_ND_ANNAHMEN_FINAL.md",
        "Extrahiere NUR ANNAHMEN, HYPOTHESEN und PSYCHOLOGISCHE EINSCHÄTZUNGEN. Was wurde nur zwischen den Zeilen angedeutet? Wo vermutet das System Trauma, Überlastung oder Dissonanz?"
    )

if __name__ == "__main__":
    main()
