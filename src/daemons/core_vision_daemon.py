# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Vision Daemon (The All-Seeing Eye)
----------------------------------------
Observer-Logik: "Sehen ist Handeln." (Quantum Observer Effect)

SCOUT-FUSION Update: Ephemeral Agent Integration
- Bei Symmetriebruch: Ephemeral Agent VISION_ANALYSIS spawnen
- Output an Vision Analyst weiterleiten

Funktion:
1. Ueberwacht RTSP-Stream (Brio/Go2RTC).
2. Erkennt Symmetrie-Brueche (Motion Detection).
3. Spawnt Ephemeral Agent fuer Gemini Vision Analyse.
4. Schreibt in ChromaDB context field.

Konstanten:
- PHI (1.618): Taktgeber für Cooldowns.
- SYMMETRY_BREAK (0.49): Schwelle für Bewegung.
"""

import cv2
import time
import os
import datetime
import threading
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from src.network.chroma_client import add_context_observation
from src.utils.time_metric import asym_sleep_float, asym_sleep_prime, asym_sleep_float_async, asym_sleep_prime_async, get_friction_timeout

# Lade Umgebungsvariablen
load_dotenv("c:/CORE/.env")

# Konfiguration
RTSP_URL = os.getenv("CORE_RTSP_URL", "rtsp://192.168.178.54:8554/mx_brio")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash-exp"  # Schnellstes Modell für Vision

# Physik-Konstanten
PHI = 1.6180339887
SYMMETRY_BREAK_THRESHOLD = 5000  # Pixel-Differenz-Area (angepasst an Brio 4K/1080p)
COOLDOWN_SECONDS = 5 * PHI  # ca. 8 Sekunden

class MthoVisionDaemon:
    def __init__(self):
        self.running = False
        self.cap = None
        self.last_observation_time = 0
        self.setup_gemini()

    def setup_gemini(self):
        if not GEMINI_API_KEY:
            print("[CRITICAL] GOOGLE_API_KEY fehlt in .env")
            return
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)
        print(f"[INIT] Gemini {MODEL_NAME} bereit.")

    def analyze_frame(self, frame):
        """Sendet Frame an Gemini zur Analyse (Legacy, direkt)."""
        try:
            import PIL.Image
            color_coverted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = PIL.Image.fromarray(color_coverted)

            prompt = (
                "CORE SYSTEM MESSAGE: Describe what you see in this security feed. "
                "Focus on movement, changes, or anomalies. Be extremely concise (1 sentence). "
                "If nothing important is happening, say 'No significant entropy'."
            )

            print("[VISION] Sende Frame an Gemini...")
            start_t = time.time()
            response = self.model.generate_content([prompt, pil_image])
            duration = time.time() - start_t

            text = response.text.strip()
            print(f"[VISION] Gemini Output ({duration:.2f}s): {text}")

            if "No significant entropy" not in text:
                try:
                    asyncio.run(add_context_observation(text, metadata={"duration_sec": duration, "model": MODEL_NAME}))
                    print("[CONTEXT] Beobachtung gespeichert.")
                except Exception as ctx_err:
                    print(f"[CONTEXT] Persist fehlgeschlagen: {ctx_err}")
                self._notify_vision_analyst(text, duration)
                self._forward_to_oc_brain(text, duration)

        except Exception as e:
            print(f"[ERROR] Vision API Fehler: {e}")

    def _notify_vision_analyst(self, analysis: str, duration: float):
        """
        SCOUT-FUSION: Benachrichtigt Vision Analyst ueber Vision Event.
        Spawnt optional TTS Worker fuer wichtige Events.
        """
        try:
            keywords_critical = ["person", "motion", "movement", "someone", "intruder"]
            is_critical = any(kw in analysis.lower() for kw in keywords_critical)

            if is_critical:
                print(f"[VISION-ANALYST] Kritisches Event: {analysis[:80]}...")
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self._spawn_tts_worker(analysis))
                    else:
                        loop.run_until_complete(self._spawn_tts_worker(analysis))
                except RuntimeError:
                    asyncio.run(self._spawn_tts_worker(analysis))
        except Exception as e:
            print(f"[VISION-ANALYST] Notification Fehler: {e}")

    def _forward_to_oc_brain(self, analysis: str, duration: float):
        """Sendet Vision-Analyse (Text, kein Base64) an OC Brain (non-blocking)."""
        def _do_forward():
            try:
                from src.network.openclaw_client import send_event_to_oc_brain

                event_data = {
                    "analysis": analysis,
                    "duration_sec": round(duration, 2),
                    "model": MODEL_NAME,
                    "source": "vision_daemon",
                }
                timeout_friction = get_friction_timeout(10.0)
                ok, resp = send_event_to_oc_brain(
                    event_type="VISION_ALERT",
                    data=event_data,
                    timeout=timeout_friction,
                )
                if ok:
                    print(f"[OC-BRAIN] Vision event forwarded: {resp[:60]}...")
                else:
                    print(f"[OC-BRAIN] Forward failed: {resp}")
            except Exception as e:
                print(f"[OC-BRAIN] Forward error: {e}")

        threading.Thread(target=_do_forward, daemon=True).start()

    async def _spawn_tts_worker(self, analysis: str):
        """Spawnt Ephemeral Agent fuer TTS-Ausgabe bei kritischem Vision Event."""
        try:
            from src.agents.core_agent import IntentType, get_ephemeral_pool
            from src.agents.scout_core_handlers import register_all_handlers

            pool = get_ephemeral_pool()
            if not pool._handlers:
                register_all_handlers(pool)

            tts_text = f"Achtung: {analysis[:100]}"
            result = await pool.spawn_and_execute(
                IntentType.TTS_DISPATCH,
                {"text": tts_text, "target": "mini"},
                ttl=15.0
            )
            print(f"[EPHEMERAL-TTS] {'OK' if result.success else 'FAIL'}: {result.duration_ms:.0f}ms")
        except Exception as e:
            print(f"[EPHEMERAL-TTS] Spawn Fehler: {e}")

    def run(self):
        print(f"[START] Verbinde zu RTSP: {RTSP_URL}")
        self.cap = cv2.VideoCapture(RTSP_URL)

        if not self.cap.isOpened():
            print("[ERROR] Konnte RTSP Stream nicht oeffnen.")
            return

        self.running = True

        # Motion Detection Init
        ret, frame1 = self.cap.read()
        ret, frame2 = self.cap.read()

        if not ret:
            print("[ERROR] Keine Frames empfangen.")
            return

        print("[RUN] Vision Loop aktiv. Warte auf Symmetrie-Bruch (Bewegung)...")

        while self.running and self.cap.isOpened():
            # Frame Differenz
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) < SYMMETRY_BREAK_THRESHOLD:
                    continue
                motion_detected = True
                break

            now = time.time()
            if motion_detected:
                time_since_last = now - self.last_observation_time
                if time_since_last > COOLDOWN_SECONDS:
                    print(f"[EVENT] Bewegung erkannt (Delta > {SYMMETRY_BREAK_THRESHOLD}). Analyse...")
                    # Wir nehmen frame2 für die Analyse
                    threading.Thread(target=self.analyze_frame, args=(frame2.copy(),)).start()
                    self.last_observation_time = now

            # Frame Shift
            frame1 = frame2
            ret, frame2 = self.cap.read()

            if not ret:
                print("[WARN] Stream unterbrochen. Reconnect...")
                self.cap.release()
                asym_sleep_prime(2)  # Reconnect asymmetrisch verzögern (Primzahl 2)
                self.cap = cv2.VideoCapture(RTSP_URL)
                ret, frame1 = self.cap.read()
                ret, frame2 = self.cap.read()

            # CPU schonen - Asymmetrische Kaskerade
            asym_sleep_float(0.05)

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    daemon = MthoVisionDaemon()
    daemon.run()
