"""
WhatsApp Audio Processor
Decrypts WhatsApp E2E audio → uploads to Gemini → returns analysis
"""
import os
import base64
import hashlib
import hmac
import struct
import tempfile
import requests
from loguru import logger
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"

# ─── WhatsApp Media Decryption (Baileys-compatible) ─────────────────────────

def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Expand as per RFC 5869"""
    n = (length + 31) // 32
    okm = b""
    t = b""
    for i in range(1, n + 1):
        t = hmac.new(prk, t + info + struct.pack("B", i), hashlib.sha256).digest()
        okm += t
    return okm[:length]

def _hkdf_extract(salt: bytes | None, ikm: bytes) -> bytes:
    if salt is None:
        salt = bytes(32)
    return hmac.new(salt, ikm, hashlib.sha256).digest()

MEDIA_TYPE_KEYS = {
    "audio": b"WhatsApp Audio Keys",
    "ptt": b"WhatsApp Audio Keys",
    "image": b"WhatsApp Image Keys",
    "video": b"WhatsApp Video Keys",
    "document": b"WhatsApp Document Keys",
}

def decrypt_whatsapp_media(encrypted_bytes: bytes, media_key_b64: str, media_type: str = "audio") -> bytes:
    """
    Decrypts WhatsApp E2E-encrypted media using HKDF + AES-256-CBC.
    Returns raw audio bytes (ogg/opus).
    """
    from Crypto.Cipher import AES
    
    media_key = base64.b64decode(media_key_b64 + "==")  # pad if needed
    info = MEDIA_TYPE_KEYS.get(media_type, b"WhatsApp Audio Keys")
    
    prk = _hkdf_extract(None, media_key)
    key_material = _hkdf_expand(prk, info, 112)
    
    iv = key_material[0:16]
    cipher_key = key_material[16:48]
    # mac_key = key_material[48:80]  # for integrity check (skipped for speed)
    
    # Remove 10-byte MAC suffix
    enc_data = encrypted_bytes[:-10]
    
    cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(enc_data)
    
    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    return decrypted[:-pad_len]


# ─── Gemini Analysis Pipeline ────────────────────────────────────────────────

PROMPT_ARCHIVIST = """Du bist der Data Archivist. 
Transkribiere diese WhatsApp-Sprachnachricht vollständig und genau. 
Behalte alle Details, Pausen, Füllwörter und emotionalen Nuancen bei.
Gib nur die Transkription zurück, keine Kommentare."""

PROMPT_ANALYST = """Du bist der ND Analyst im ATLAS-System.
Basierend auf dieser Transkription einer WhatsApp-Sprachnachricht:
1. Extrahiere alle Aufgaben, Erinnerungen oder To-Dos
2. Identifiziere den emotionalen Zustand des Sprechers
3. Fasse die Kernaussage in 1-2 Sätzen zusammen

Format:
📝 ZUSAMMENFASSUNG: ...
✅ AUFGABEN: ...
💬 KERNAUSSAGE: ..."""


async def process_whatsapp_audio(audio_msg: dict, sender: str) -> str:
    """
    Full pipeline: Download → Decrypt → Upload to Gemini → Analyze → Return summary
    """
    url = audio_msg.get("url", "")
    media_key = audio_msg.get("mediaKey", "")
    mimetype = audio_msg.get("mimetype", "audio/ogg; codecs=opus")
    seconds = audio_msg.get("seconds", 0)
    
    if not url or not media_key:
        return "❌ Keine Audio-URL oder Key vorhanden."
    
    logger.info(f"Starte Audio-Pipeline: {seconds}s Audio von {sender}")
    
    try:
        # 1) Download verschlüsseltes Audio
        logger.info(f"Lade Audio herunter: {url[:60]}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        encrypted_bytes = resp.content
        logger.info(f"Heruntergeladen: {len(encrypted_bytes)} Bytes")
        
        # 2) Entschlüsseln
        logger.info("Entschlüssele Audio (AES-256-CBC)...")
        audio_bytes = decrypt_whatsapp_media(encrypted_bytes, media_key, "audio")
        logger.info(f"Entschlüsselt: {len(audio_bytes)} Bytes ogg/opus")
        
        # 3) Temporäre Datei schreiben
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        # 4) Zu Gemini hochladen
        logger.info("Lade Audio zu Gemini hoch...")
        uploaded = client.files.upload(file=tmp_path)
        logger.info(f"Gemini Upload: {uploaded.uri}")
        os.unlink(tmp_path)
        
        # 5) Transkription
        logger.info("Schritt 1: Transkription (Archivist)...")
        r1 = client.models.generate_content(
            model=MODEL,
            contents=[uploaded, PROMPT_ARCHIVIST],
            config=types.GenerateContentConfig(temperature=0.1)
        )
        transcript = r1.text
        logger.success(f"Transkription: {transcript[:100]}...")
        
        # 6) Analyse
        logger.info("Schritt 2: Analyse (ND Analyst)...")
        r2 = client.models.generate_content(
            model=MODEL,
            contents=[PROMPT_ANALYST, f"TRANSKRIPTION:\n{transcript}"],
            config=types.GenerateContentConfig(temperature=0.2)
        )
        analysis = r2.text
        logger.success("Analyse abgeschlossen!")
        
        # Cleanup Gemini file
        client.files.delete(name=uploaded.name)
        
        return analysis
        
    except ImportError:
        return "⚠️ pycryptodome nicht installiert! `pip install pycryptodome`"
    except requests.RequestException as e:
        logger.error(f"Download fehlgeschlagen: {e}")
        return f"❌ Audio-Download fehlgeschlagen: {e}"
    except Exception as e:
        logger.error(f"Audio-Pipeline Fehler: {e}")
        return f"❌ Verarbeitungsfehler: {e}"
