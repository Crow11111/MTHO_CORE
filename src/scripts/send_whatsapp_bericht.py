"""
Sendet einen Zwischenbericht an Marc via WhatsApp (ueber HAClient).
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, "c:/ATLAS_CORE")
from src.network.ha_client import HAClient


def main() -> int:
    load_dotenv("c:/ATLAS_CORE/.env")
    target = (os.getenv("WHATSAPP_TARGET_ID") or "").strip()
    if not target:
        print("FEHLER: WHATSAPP_TARGET_ID in .env nicht gesetzt.")
        return 1

    text = "Hallo Marc, hier ist der Dev-Agent. Ich beginne jetzt mit der genauen Überprüfung des neuen OC Brains (Admin). Ich habe bereits die Gemini-API und die interne Struktur getestet (Modell: Gemini 3.1 Pro ist aktiv, Local Memory wurde übertragen). WhatsApp-Plugin ist ebenfalls auf dem neuen Container aktiviert und greift auf die alte Session zu. Ich überprüfe jetzt die Kommunikation mit ChromaDB und den restlichen Netzwerken, bevor ich die Migration finalisiere."
    
    print(f"Sende WhatsApp an {target!r} ...")

    ha = HAClient()
    ok = ha.send_whatsapp(to_number=target, text=text)
    print("Ergebnis:", "OK" if ok else "FEHLER")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
