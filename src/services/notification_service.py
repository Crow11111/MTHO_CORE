# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class WhatsAppNotificationService:
    def __init__(self):
        self.api_version = "v18.0"
        self._token: Optional[str] = None
        self._phone_id: Optional[str] = None
        self._target_phone: Optional[str] = None
        self._base_url: Optional[str] = None

    def _load_env(self):
        self._token = os.getenv("WHATSAPP_TOKEN")
        self._phone_id = os.getenv("WHATSAPP_PHONE_ID")
        self._target_phone = os.getenv("WHATSAPP_TARGET_PHONE")
        if self._phone_id:
            self._base_url = f"https://graph.facebook.com/{self.api_version}/{self._phone_id}/messages"

    async def send_text_message(self, to: str, text: str) -> bool:
        self._load_env()
        
        if not self._token or not self._base_url:
            logger.error("WHATSAPP_TOKEN oder WHATSAPP_PHONE_ID fehlen in .env")
            return False

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        # Strikte Nutzung von async http client, keine synchronen blockierenden Calls
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self._base_url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"WhatsApp message successfully sent to {to}")
                return True
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API HTTP Error: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"Exception during WhatsApp message send: {str(e)}")
                return False

    async def _upload_media(self, audio_bytes: bytes, mime_type: str = "audio/mpeg") -> Optional[str]:
        if not self._token or not self._phone_id:
            logger.error("WhatsApp credentials missing for upload")
            return None
            
        url = f"https://graph.facebook.com/{self.api_version}/{self._phone_id}/media"
        headers = {
            "Authorization": f"Bearer {self._token}"
        }
        files = {
            "file": ("audio.mp3", audio_bytes, mime_type)
        }
        data = {
            "messaging_product": "whatsapp"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, data=data, files=files)
                response.raise_for_status()
                return response.json().get("id")
            except Exception as e:
                logger.error(f"Media Upload Fehler: {str(e)}")
                return None

    async def send_audio_message(self, to: str, audio_bytes: bytes) -> bool:
        self._load_env()
        
        if not self._token or not self._base_url:
            logger.error("WHATSAPP_TOKEN oder WHATSAPP_PHONE_ID fehlen in .env")
            return False
            
        media_id = await self._upload_media(audio_bytes)
        if not media_id:
            logger.error("Audio Upload fehlgeschlagen, sende keine Nachricht.")
            return False

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "audio",
            "audio": {
                "id": media_id
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self._base_url, headers=headers, json=payload)
                response.raise_for_status()
                logger.info(f"WhatsApp audio successfully sent to {to}")
                return True
            except Exception as e:
                logger.error(f"WhatsApp Audio Send Fehler: {str(e)}")
                return False

    async def notify_hardware_request(self, reason: str, expected_roi: str) -> bool:
        self._load_env()
        
        if not self._target_phone:
            logger.error("WHATSAPP_TARGET_PHONE ist nicht konfiguriert")
            return False

        message = (
            f"⚠️ *CORE SYSTEM REQUEST*\n\n"
            f"*Typ:* Hardware Expansion\n"
            f"*Grund:* {reason}\n"
            f"*Erwarteter ROI:* {expected_roi}\n\n"
            f"Bitte via System Console genehmigen oder ablehnen."
        )
        return await self.send_text_message(to=self._target_phone, text=message)

# Singleton Instanz für einfachen Import
notification_service = WhatsAppNotificationService()
