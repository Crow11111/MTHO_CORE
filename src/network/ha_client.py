from loguru import logger
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

class HAClient:
    def __init__(self):
        self.base_url = os.getenv("HASS_URL")
        self.token = os.getenv("HASS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def send_whatsapp(self, to_number: str, text: str) -> bool:
        url = f"{self.base_url}/api/services/whatsapp/send_message"
        payload = {
            "clientId": "default",
            "to": to_number,
            "body": {"text": text}  # ← WhatsApp add-on expects nested body: {text: str}
        }
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=5, verify=False)
            r.raise_for_status()
            logger.info("WhatsApp Nachricht via HA gesendet an {}", to_number)
            return True
        except Exception as e:
            logger.error("Fehler beim Senden der WhatsApp Nachricht: {}", e)
            return False

    def send_whatsapp_audio(self, to_number: str, audio_path: str, host_ip: str = None, port: int = 8002) -> bool:
        """
        Sendet eine lokale Audiodatei als WhatsApp Sprachnachricht (PTT).
        Startet kurz einen HTTP-Server damit der Pi die Datei laden kann.
        """
        import threading, time, os
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        
        host_ip = host_ip or os.getenv("ATLAS_HOST_IP", "192.168.178.110")
        filename = os.path.basename(audio_path)
        serve_dir = os.path.dirname(os.path.abspath(audio_path))
        audio_url = f"http://{host_ip}:{port}/{filename}"
        
        # Kurzer HTTP Server
        orig_dir = os.getcwd()
        os.chdir(serve_dir)
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()
        time.sleep(0.5)
        
        try:
            url = f"{self.base_url}/api/services/whatsapp/send_message"
            r = requests.post(url, headers=self.headers, json={
                "clientId": "default",
                "to": to_number,
                "body": {"audio": {"url": audio_url}, "ptt": True}
            }, timeout=15, verify=False)
            r.raise_for_status()
            logger.info("WhatsApp Audio via HA gesendet an {}", to_number)
            return True
        except Exception as e:
            logger.error("Fehler beim Senden von WhatsApp Audio: {}", e)
            return False
        finally:
            time.sleep(3)
            server.shutdown()
            os.chdir(orig_dir)

    def send_mobile_app_notification(self, text: str, title: str = "ATLAS_CORE") -> bool:
        url = f"{self.base_url}/api/services/notify/mobile_app_iphone_von_mth"
        payload = {
            "message": text,
            "title": title,
            "data": {
                "data": {
                    "actions": [
                        {
                            "action": "atlas_ping",
                            "title": "Ping an ATLAS"
                        }
                    ]
                }
            }
        }
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=5, verify=False)
            logger.info("Mobile Backup-Notification gesendet.")
            return True
        except Exception as e:
            logger.error("Fehler bei Backup-Notification: {}", e)
            return False

    def call_service(self, domain: str, service: str, entity_id: str = None, service_data: dict = None) -> bool:
        """
        Calls a generic Home Assistant service (e.g. light/turn_on).
        """
        url = f"{self.base_url}/api/services/{domain}/{service}"
        payload = service_data or {}
        if entity_id:
            payload["entity_id"] = entity_id
            
        try:
            r = requests.post(url, headers=self.headers, json=payload, timeout=5, verify=False)
            r.raise_for_status()
            logger.info("HA Service {}.{} für {} ausgeführt", domain, service, entity_id)
            return True
        except Exception as e:
            logger.error("Fehler bei HA Service Aufruf: {}", e)
            return False

if __name__ == "__main__":
    ha = HAClient()
    ha.send_mobile_app_notification("WhatsApp Brücke wurde soeben durch ATLAS konzeptioniert. Bitte prüfe den ATLAS Chat für weitere Schritte zu HTTPS und WhatsApp Nummer.")
