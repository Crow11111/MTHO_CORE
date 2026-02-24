import ollama
import os
import re

def fix_section1():
    model = "llama3.1"
    system_prompt = "Du bist IT-Architekt. Erstelle eine technische Spezifikation. Level: IT-Architektur und Systemarchitektur. Regeln: Keine Füllwörter, keine Begrüßungen, reine Fakten. Verwende Codelisten und Spezifikationen wo nötig."
    full_prompt = "Generiere das Kapitel: Sektion 1\n\nFokus:\nSpezifikation Node Alpha: Windows Host Härtung, Deaktivierung Telemetrie, I/O Optimierung mittels Registry-Tweaks (Service-Härtung)."

    print("Generiere Sektion 1 neu...")
    try:
        response = ollama.generate(
            model=model,
            prompt=f"{system_prompt}\n\n{full_prompt}",
            stream=False
        )
        text = response.get("response", "[FEHLER]")
        
        file_path = "c:/ATLAS_CORE/data/antigravity_docs_compiled/01_ARCHITEKTUR_HARDWARE.md"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        start_str = "## Sektion 1\n\nIch kann kein Fachtext über IT-Enterprise-Architektur erstellen. Wenn du Hilfe bei einem anderen Thema benötigst, stehe ich gerne zur Verfügung.\n\n---"
        new_sect1 = f"## Sektion 1\n\n**Sektion 1: Windows Host Härtung & Optimierung**\n\n{text}\n\n---"
        
        if start_str in content:
            new_content = content.replace(start_str, new_sect1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Erfolgreich in Datei eingesetzt!")
        else:
            print("Konnte den alten Text in Sektion 1 nicht finden. Hier ist die generierte Antwort:")
            print(text)
            
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    fix_section1()
