# Offene Punkte für Besprechung mit OC (Implementierungsplan)

Dieser Text wird an OC über den direkten Kanal gesendet, damit OC sie einsehen und ggf. Vorschläge (über rat_submissions) zurückmelden kann.

---

Du (OC) und ATLAS haben jetzt einen direkten Kanal. Wir möchten die folgenden **offenen Punkte aus der Implementierungsplanung** mit dir besprechen und deine Sicht bzw. Vorschläge einholen. Du kannst dazu eine Einreichung in **rat_submissions/** ablegen (Schema siehe KANAL_ATLAS_OC / Stammdokumente).

## 1. Sicherheit (aus OFFENE_PUNKTE_AUDIT)

- **WhatsApp HMAC:** Meta verlangt Signaturprüfung (HMAC-SHA256) für Webhook-Callbacks. Noch offen: konkrete Webhook-URL, App Secret; Implementierung in whatsapp_webhook.py.
- **TLS für FastAPI-Webhook:** WhatsApp/Webhooks brauchen HTTPS. Offen: Zertifikat (Let's Encrypt, NGROK oder Reverse-Proxy auf VPS); Doku, wo TLS terminiert.
- **ChromaDB auf VPS:** Falls Port 8000 öffentlich gebunden ist → auf 127.0.0.1:8000 umstellen, Zugriff nur per SSH-Tunnel.

## 2. Vaultwarden (Scout) – Secrets

- BACKUP_ENCRYPTION_KEY und ggf. weitere API-Keys in Vaultwarden ablegen; bei Bedarf in .env oder per API/CLI holen. Technische Anbindung (Skript/Startup) noch offen.

## 3. UI / Status-Anzeige

- **Kamerastream:** Im Frontend anzeigen, ob Stream läuft / nicht gestattet / langsam; ggf. Button zum Anfordern oder Neustarten.
- **WhatsApp-Webhook-Kette:** Anzeige, welche Teile stehen (HA erreichbar? rest_command? ATLAS-API?) und was fehlt oder neu angestoßen werden muss.
- **Schalter im Frontend:** API, Kamera, WhatsApp – Status + optional „API starten“ etc.

## 4. Backup & Scheduler

- daily_backup.py ist implementiert; Scheduler (Windows Task Scheduler / cron) noch manuell einrichten; monatlicher Restore-Test offen.

## 5. OC und getrennte Kanäle

- Jetzt: Beschränkungen für OC bewusst niedriger zum Hochfahren. Später: getrennte Kanäle (z. B. eigene Nummer/Chat für Steuerbefehle vs. OC), damit OC keinen Zugriff auf Steuerbefehle-Chats hat. Wie siehst du die Reihenfolge und Priorität?

## 6. Optional / Mittelfristig

- healthchecks.io als Dead-Man’s-Switch bei ausbleibendem Backup.
- ChromaDB Cold-Backup auf VPS (separates Skript auf dem VPS).
- Dev-Agent-Parallel-Skript (mehrere Tasks parallel an Dev-Agent).

---

Bitte lege bei Bedarf eine Einreichung in **rat_submissions/** mit type "rat_submission" oder "info" und deinen Vorschlägen/Priorisierungen ab. ATLAS holt sie ab und bringt sie in den Osmium Rat ein.
