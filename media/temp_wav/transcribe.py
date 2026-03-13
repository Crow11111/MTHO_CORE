from faster_whisper import WhisperModel
import os, time

model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model loaded successfully")

wav_dir = r"c:\CORE\media\temp_wav"
files = sorted([f for f in os.listdir(wav_dir) if f.endswith(".wav")])

for f in files:
    filepath = os.path.join(wav_dir, f)
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"FILE: {f}")
    print(sep)
    start = time.time()
    segments, info = model.transcribe(filepath, language="de", beam_size=5)
    print(f"Language: {info.language} (prob: {info.language_probability:.2f})")
    print(f"Duration: {info.duration:.1f}s")
    print("---TRANSCRIPT---")
    full_text = []
    for seg in segments:
        text = seg.text.strip()
        full_text.append(text)
        print(f"[{seg.start:.1f}s-{seg.end:.1f}s] {text}")
    elapsed = time.time() - start
    print(f"---END--- (processed in {elapsed:.1f}s)")
    print(f"FULL: {' '.join(full_text)}")
