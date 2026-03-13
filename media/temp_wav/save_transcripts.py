from faster_whisper import WhisperModel
import os, time

model = WhisperModel("base", device="cpu", compute_type="int8")

wav_dir = r"c:\CORE\media\temp_wav"
out_file = r"c:\CORE\media\temp_wav\transkriptionen.txt"
files = sorted([f for f in os.listdir(wav_dir) if f.endswith(".wav")])

with open(out_file, "w", encoding="utf-8") as out:
    for f in files:
        filepath = os.path.join(wav_dir, f)
        segments, info = model.transcribe(filepath, language="de", beam_size=5)
        out.write(f"\n{'='*60}\n")
        out.write(f"DATEI: {f}\n")
        out.write(f"Dauer: {info.duration:.1f}s | Sprache: {info.language} ({info.language_probability:.2f})\n")
        out.write(f"{'='*60}\n\n")
        full_text = []
        for seg in segments:
            text = seg.text.strip()
            full_text.append(text)
            out.write(f"[{seg.start:.1f}s - {seg.end:.1f}s] {text}\n")
        out.write(f"\nVOLLTEXT:\n{' '.join(full_text)}\n\n")

print(f"Saved to {out_file}")
