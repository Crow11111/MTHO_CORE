import openwakeword
import os
import shutil
import sys
import argparse

def main():
    print("=== ATLAS Wake Word Trainer ===")
    
    # Pfade
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    pos_dir = os.path.join(base_dir, "data", "positive")
    neg_dir = os.path.join(base_dir, "data", "negative")
    model_dir = os.path.join(base_dir, "models")
    
    os.makedirs(model_dir, exist_ok=True)
    
    # Dateien laden
    pos_clips = [os.path.join(pos_dir, f) for f in os.listdir(pos_dir) if f.endswith(".wav")]
    neg_clips = [os.path.join(neg_dir, f) for f in os.listdir(neg_dir) if f.endswith(".wav")]
    
    if len(pos_clips) < 3:
        print("FEHLER: Zu wenige positive Beispiele (mindestens 3).")
        sys.exit(1)
        
    print(f"Lade {len(pos_clips)} positive und {len(neg_clips)} negative Beispiele...")
    
    output_path = os.path.join(model_dir, "atlas_custom_verifier.pkl")
    tflite_path = os.path.join(model_dir, "atlas_custom_verifier.tflite")
    onnx_path = os.path.join(model_dir, "atlas_custom_verifier.onnx")

    try:
        print("Starte Training (kann 1-2 Minuten dauern)...")
        
        # Training
        model = openwakeword.train_custom_verifier(
            positive_reference_clips=pos_clips,
            negative_reference_clips=neg_clips if neg_clips else [],
            output_path=output_path,
            model_name="atlas_verifier"
        )
        
        print("Training erfolgreich!")
        print(f"Modell gespeichert: {output_path}")
        
        # Versuche Export als ONNX/TFLite (falls openwakeword das nicht automatisch macht)
        # Hinweis: openwakeword.train_custom_verifier speichert oft .pkl
        # Aber Home Assistant Addons nutzen oft TFLite.
        # Wenn wir nur .pkl haben, ist das okay, wenn das Addon das unterstützt.
        # Aber um sicher zu gehen, kopieren wir es auch als .tflite falls es so rauskommt.
        
        # Prüfen was erzeugt wurde
        if os.path.exists(output_path):
             print(f"Modell ist bereit: {os.path.basename(output_path)}")
        
        # Optional: Konvertierung zu TFLite (falls möglich/nötig)
        # Hier lassen wir es erstmal bei PKL/ONNX.
        
    except Exception as e:
        print(f"FEHLER beim Training: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
