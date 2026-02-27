import os
import ollama
from loguru import logger

MODEL = "llama3.1"
SOURCE_DIR = r"c:\ATLAS_CORE\data\antigravity_docs_compiled"
OUTPUT_DIR = r"c:\ATLAS_CORE\data\antigravity_docs_osmium"
GOLD_DOC = r"c:\ATLAS_CORE\docs\01_CORE_DNA\nd_insights_v4\ATLAS_ND_PROFILE_GOLD.md"

def load_gold_rules():
    if not os.path.exists(GOLD_DOC):
        logger.error("Gold Document nicht gefunden!")
        return ""
    with open(GOLD_DOC, "r", encoding="utf-8") as f:
        # We limit the gold rules slightly if they are massive to avoid context overflow, 
        # but 3000 chars is usually just the summary anyway.
        return f.read()

def rewrite_doc_osmium(filename, content, gold_rules):
    # System prompt integrating the entire overarching council
    system_prompt = f"""Du bist ein reiner technischer Dokumentations-Compiler. Es gibt keine Konversation, keine Entschuldigungen. Übersetze und erweitere das Lastenheft EXAKT nach den folgenden Vorgaben als reines Markdown-Dokument. Beginne sofort mit der '# ' Überschrift.

DEINE AUFGABE als 'Osmium Council' (ND_THERAPIST, NT_SPECIALIST, UNIVERSAL_BOARD):
Umschreiben dieses IT-Architektur-Lastenhefts, sodass die systemischen Erkenntnisse von Marcs hochgradigem Monotropismus (AuDHD) organisch auf Hardware-, Datenbank- und API-Ebene verankert werden.

REGELN DES OSMIUM COUNCILS (STRIKTE PRIORITÄT):
1. [PRIO 1] ND_THERAPIST: Jegliche "Kognitive Reibung" für Marc muss technisch minimiert werden (z.B. offene Eingangsschwellen, Modulare UI). 
2. [PRIO 2] NT_SPECIALIST: Schnittstellen, die mit der neurotypischen Welt interagieren, müssen bidirektionale Übersetzungslogik aufweisen.
3. [PRIO 3] UNIVERSAL_BOARD: Veto-Recht zur Optimierung von KI-Tokens, Hardware-Kosten und Umwelteinfluss. Halte es effizient.

MARCS KOGNITIVES GOLD-PROFIL:
{gold_rules[:6000]}

ANWEISUNG ZUR BEARBEITUNG:
- Behalte ALLE technischen Eckdaten, Hardware-Spezifikationen und Architekturen bei.
- Füge ein Kapitel ein: "Osmium Council Revision", in dem die Regeln angewendet werden.
- Formatiere als reines Markdown. Mache keine einleitenden Sätze wie "Hier ist das Dokument". Starte sofort mit dem Markdown-Inhalt.
"""
    
    prompt = f"BASIS-DOKUMENT ({filename}):\n\n{content}"
    
    # We send the request directly to Llama 3.1
    response = ollama.generate(model=MODEL, prompt=f"{system_prompt}\n\n{prompt}", stream=False)
    return response.get("response", "[FEHLER BEI DER GENERIERUNG]")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    gold_rules = load_gold_rules()
    if not gold_rules:
        return
        
    # Process every markdown file in the compiled docs folder
    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".md"): 
            continue
            
        source_path = os.path.join(SOURCE_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename.replace(".md", "_OSMIUM.md"))
        
        logger.info(f"Start Osmium-Aufwertung (Council-Review) für: {filename}")
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_content = rewrite_doc_osmium(filename, content, gold_rules)
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        logger.success(f"OSMIUM-Standard gespeichert: {out_path}")

if __name__ == "__main__":
    main()
