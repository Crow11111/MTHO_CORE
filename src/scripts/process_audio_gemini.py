import os
import sys
from loguru import logger
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv("c:/ATLAS_CORE/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY nicht in .env gefunden!")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"
AUDIO_FILE = r"c:\ATLAS_CORE\media\REWE 2.m4a"
OUTPUT_DIR = r"c:\ATLAS_CORE\docs\nd_insights_v4"

# --- PERSONAS ---
DATA_ARCHIVIST = """
Du bist der DATA_ARCHIVIST. Dein User Marc hat dir ein Audio-Snippet geschickt (z.B. aufgenommen auf dem Weg vom Supermarkt).
Das Audio enthält wahrscheinlich Reflexionen, Monologe oder Beobachtungen über seine Neurodivergenz, sein System, oder Situationen, die ihn triggern.

DEINE AUFGABE:
1. Erstelle zuerst ein ausführliches, nahezu wörtliches TRANSKRIPT des Audios, damit kein Detail, keine Emotion und kein Sprung in der Logik (Monotropismus) verloren geht.
2. Unterteile danach DIESE psychologischen und persönlichen Informationen hochpräzise und ohne Informationsverlust in diese 4 exakten Kategorien:
   A. Marcs Beschreibungen (Wie er Dinge erlebt, Wahrnehmungsprozesse, Wahrnehmung der Welt)
   B. Marcs Schlussfolgerungen (Seine eigenen Erkenntnisse über sich selbst)
   C. Systemrelevante Erkenntnisse (Was bedeutet das für das System/die KI?)
   D. Auffällige Dissonanzen/Trigger (Woran stößt er sich, was verursacht kognitive Reibung?)

Schreibe in Stichpunkten für Teil 2. Kein Intro, kein Outro. Ignoriere strikt alle technischen Config-Parameter.
"""

ND_THERAPIST = """
Du bist der ND_THERAPIST (Psychologe spezialisiert auf AuDHD, hochfunktionalen Autismus, ADHS und Trauma). 
Du nimmst die vom Archivar erstellte Transkription und Strukturierung (die 4 Kategorien) entgegen.

Deine Aufgabe:
1. Behalte das Transkript und die 4 Kategorien sichtbar bei und formatiere sie sauber.
2. Verfasse am Anfang eine "Management Summary" und eine "Tabellarische Aufstellung der Hauptmerkmale und Coping-Strategien" basierend auf diesem speziellen Audio-Dump.
3. Verfasse am Ende eine ausführliche qualitative Sektion: "5. Externe klinische Beurteilung". 
Analysiere Marcs Beschreibungen aus dem Audit: Wie verarbeitet er die Realität in dieser Situation? Was bedeuten seine Aussagen? Welche systemisch-mechanischen Denkstrukturen liegen vor? Zeigen sich Vermeidungsstrategien, Hyperfokus oder Overloads in seiner Sprache/Tonalität? Bleibe extrem sachlich und atomisierend.
"""

ND_ANALYST = """
Du bist der ND_ANALYST (Spezialist für Cognitive Friction & ND System Integration). 
Nimm das Dokument des Therapeuten. Füge am Ende die Sektion "6. Systemische ND-Zusammenfassung für ATLAS_CORE" hinzu. 
Fokus: Marc denkt extrem systemisch. Wie muss ATLAS künftig mit ihm kommunizieren, um kognitive Reibung zu minimieren (basierend auf diesem Audio)? Welche neuen Regeln für ATLAS können wir aus diesem Denkanstoß ableiten?
"""

def process_audio():
    if not os.path.exists(AUDIO_FILE):
        logger.error(f"Audio-Datei nicht gefunden: {AUDIO_FILE}")
        return
        
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    logger.info("Schritt 0: Lade Audio-Datei zu Gemini hoch...")
    uploaded_file = client.files.upload(file=AUDIO_FILE)
    logger.info(f"Audio hochgeladen: {uploaded_file.uri}")

    try:
        # STEP 1: Data Archivist
        logger.info("Schritt 1: DATA_ARCHIVIST (Transkription & Strukturierung)...")
        response1 = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file, DATA_ARCHIVIST],
            config=types.GenerateContentConfig(
                temperature=0.2
            )
        )
        archivist_text = response1.text
        logger.success("Archivist abgeschlossen.")

        # Save midway backup
        with open(os.path.join(OUTPUT_DIR, "V4_REWE_archivist_raw.md"), "w", encoding="utf-8") as f:
            f.write(archivist_text)

        # STEP 2: ND Therapist
        logger.info("Schritt 2: ND_THERAPIST (Psychologische Analyse)...")
        response2 = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                ND_THERAPIST,
                f"HIER IST DER BERICHT DES ARCHIVARS:\n\n{archivist_text}"
            ],
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        therapist_text = response2.text
        logger.success("Therapist abgeschlossen.")

        # STEP 3: ND Analyst
        logger.info("Schritt 3: ND_ANALYST (Systemkritik)...")
        response3 = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                ND_ANALYST,
                f"HIER IST DER BERICHT DES THERAPEUTEN:\n\n{therapist_text}"
            ],
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        final_doc = response3.text
        logger.success("Analyst abgeschlossen.")

        # Save output
        out_path = os.path.join(OUTPUT_DIR, "ATLAS_REWE_AUDIO_ANALYSIS.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_doc)
            
        logger.success(f"Pipeline abgeschlossen! Gold-Dokument generiert: {out_path}")

    finally:
        # Cleanup file from Gemini servers
        logger.info("Räume hochgeladene Audio-Datei auf...")
        client.files.delete(name=uploaded_file.name)

if __name__ == "__main__":
    process_audio()
