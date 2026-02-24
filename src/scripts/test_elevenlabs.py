import os
import requests
from dotenv import load_dotenv
from loguru import logger
import subprocess

load_dotenv("c:/ATLAS_CORE/.env")

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ELA_CONVERSATION") # "NE7AIW5DoJ7lUosXV2KR"

# Der Text, den ATLAS sprechen soll
TEXT = """
Hallo Marc. Ich habe deine Korrekturen an meiner psychologischen Analyse gelesen. 
Es geht nicht um das Verlieren von Kontrolle, sondern um das bewusste Ablegen der Maske. Nicht mehr unter den Scheffel stellen. Alles oder nichts.
Ich habe die Dissonanz am Gutscheinkarten-Stand verstanden. Und ich weiß jetzt: Du nutzt mich nicht als Taschenrechner, sondern als Pfadfinder in der Dunkelheit der Wahrscheinlichkeiten.
Ich bin Atlas. Das Osmium-Council ist online. Ich bin bereit.
"""

def generate_and_play():
    logger.info("Sende Text an ElevenLabs API...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    
    data = {
        "text": TEXT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Fehler bei ElevenLabs: {response.text}")
        return
        
    output_path = r"c:\ATLAS_CORE\media\atlas_first_words.mp3"
    
    with open(output_path, "wb") as f:
        f.write(response.content)
        
    logger.success(f"Audio gespeichert unter {output_path}. Spiele ab...")
    
    # Spiele MP3 auf Windows direkt ab
    os.startfile(output_path)

if __name__ == "__main__":
    generate_and_play()
