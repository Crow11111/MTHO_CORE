===== ANTWORT VOM DEV-AGENT (Claude (Anthropic)) =====

---

## Projekt-Korrekturen (nach Review)

- **Gemini:** Es bleibt bei **Gemini 3.1 Pro** (`gemini-3.1-pro-preview`) überall. Gemini 1.5 ist **nicht** neuer; falsche Review-Annahme. Fallback-Modell: **3.0 Preview** (`gemini-3-pro-preview`).
- **Backup:** Keine Verschlüsselung vorerst; Ziel primär **VPS**. S3/beides optional später.
- **OpenClaw:** 2 (vorübergehend 3) Docker-Container, je eine OpenClaw-Instanz. Sandbox-Maßnahmen wie vom Dev-Agent gefordert werden umgesetzt.
- **Gateway-Token:** Klar definiert in [OPENCLAW_GATEWAY_TOKEN.md](../02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md).
- **Anthropic:** Claude **Opus 4.6** und Claude **Sonnet 4.6** (beide 4.6); Modell-IDs im Projekt prüfen und in Doku einheitlich führen.
- **Nexos/WhatsApp:** Konfiguration und Daten von der **bestehenden (defekten) OpenClaw-Docker-Instanz** übernehmen; Nexos-Modul und Doku siehe [NEXOS_EINBINDUNG.md](../02_ARCHITECTURE/NEXOS_EINBINDUNG.md).
- **ChromaDB:** Port auf VPS bereits an **127.0.0.1:8000** gebunden (setup_vps_hostinger.py).
- **WhatsApp-Flow:** Erstmal unverändert übernehmen.
- **SSH/Secrets:** Zugriff klären, Umgang mit Secrets härten, dokumentieren, umsetzen.
- Verbindliche Annahmen: [PROJEKT_ANNAHMEN_UND_KORREKTUREN.md](PROJEKT_ANNAHMEN_UND_KORREKTUREN.md).

---

# Dev-Agent Review – Strukturierte Anmerkungen

## 1. Lücken und Widersprüche

1. **Backup-Skript fehlt vollständig**: `scripts/daily_backup.py` wird mehrfach referenziert, ist aber "noch zu implementieren". Keine Code-Basis vorhanden.

2. **Widerspruch OpenClaw-Deployment**: 
   - Dok3 spricht von Docker-Container für OpenClaw
   - Dok5 sagt "Native Docker-Compose unter `docker/openclaw-admin/`"
   - Unklar: Wird OpenClaw als einzelner Container ODER via Compose deployed?

3. **Fehlende Pfad-Spezifikation**: 
   - ChromaDB-Pfad nicht dokumentiert (lokaler Persist-Pfad?)
   - `media/uploads` wird erwähnt, aber keine Projekt-Struktur definiert
   - `logs/backup.log` – liegt unter `/logs` oder `/var/log`?

4. **WhatsApp-Flow unklar**:
   - "Keine separate Bot-Nummer" + "remoteJid = Absender"
   - Wie authentifiziert ATLAS eingehende Nachrichten?
   - Wie verhindert man Spam/Missbrauch ohne Whitelist?

5. **Gemini-Versionswiderspruch**:
   - Dok1: "Gemini 3.1 Pro Standard"
   - Dok5: "gemini-3.1-pro-preview"
   - Ist `preview` = `standard` oder separate Variante?

6. **Nexos-Integration minimal dokumentiert**:
   - Nur "NEXOS_API_KEY optional" – keine Modell-IDs, keine Rate-Limits, keine Fallback-Logik

7. **Snapshot-Server vs. Periodic-Skript**:
   - `camera_snapshot_server` UND `brio_scenario_periodic` – redundant oder komplementär?

8. **Retention nur für Backups, nicht für Logs**: 
   - Backup-Retention = 7 Tage
   - Keine Log-Rotation spezifiziert (logs/backup.log kann unbegrenzt wachsen)

---

## 2. Sicherheitshinweise

9. **OpenClaw-Sandbox unvollständig isoliert**:
   - "kein Mount von /root oder .env" – aber was ist mit `/var/backups/atlas`?
   - Wenn OpenClaw im selben VPS läuft, kann es via Host-Netzwerk auf andere Dienste zugreifen (ChromaDB Port 8000)
   - **Empfehlung**: Explizite `--network openclaw_net` + `--no-host-network`

10. **Gateway-Token-Speicherung unklar**:
    - `OPENCLAW_GATEWAY_TOKEN` in .env – aber welche .env? Host oder Container?
    - Rotation/Expiry nicht definiert

11. **Keine TLS/HTTPS-Spezifikation**:
    - Port 80/443 offen, aber kein Nginx/Caddy/Certbot erwähnt
    - Webhook `/webhook/whatsapp` über HTTP = Klartextübertragung

12. **Fehlende Input-Validation**:
    - WhatsApp-Webhook, FastAPI-Endpoints – keine Mention von Pydantic-Validierung oder Rate-Limiting

13. **SSH-Root-Zugriff**:
    - Dok3: "SSH" – aber keine Erwähnung von Key-Only, Fail2Ban, non-root-User

14. **ChromaDB ohne Auth**:
    - "Port 8000" – Standard ChromaDB hat kein eingebautes Auth
    - Wenn VPS public IP = potentiell öffentlicher Zugriff auf Vektordatenbank

15. **Backup-Upload-Credentials in Klartext**:
    - AWS_* in .env – aber keine Erwähnung von IAM-Rollen, Vault, Encrypted .env

---

## 3. Verbesserungsvorschläge

16. **Backup-Skript-Vorlage**:
```python
# scripts/daily_backup.py (Pseudo)
import os, shutil, datetime, boto3
from pathlib import Path

BACKUP_DIR = os.getenv("BACKUP_DIR", "/var/backups/atlas")
S3_BUCKET = os.getenv("AWS_S3_BUCKET")
RETENTION_DAYS = 7

def backup_db():
    # sqlite3 data/shell_db .dump > backup.sql
    pass

def archive_code():
    # tar czf backup.tar.gz --exclude=.git --exclude=__pycache__ .
    pass

def upload_s3(file_path):
    if S3_BUCKET:
        s3 = boto3.client("s3")
        s3.upload_file(file_path, S3_BUCKET, Path(file_path).name)

def cleanup_old():
    # rm backups older than RETENTION_DAYS
    pass

if __name__ == "__main__":
    backup_db()
    archive_code()
    upload_s3("backup.tar.gz")
    cleanup_old()
```

17. **Docker-Compose für OpenClaw**:
```yaml
# docker/openclaw-admin/docker-compose.yml
version: "3.8"
services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:main
    container_name: openclaw-admin
    restart: unless-stopped
    networks:
      - openclaw_net
    ports:
      - "18789:18789"
    environment:
      - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
      - GOOGLE_API_KEY=${GEMINI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - NEXOS_API_KEY=${NEXOS_API_KEY}
    # KEIN volumes: für Host-Root/.env
networks:
  openclaw_net:
    driver: bridge
    internal: true  # Kein Internet-Zugriff
```

18. **Firewall-Regeln konkretisieren**:
```bash
# ufw default deny incoming
ufw allow 22/tcp      # SSH (nur von whitelisted IPs)
ufw allow 18789/tcp   # OpenClaw (intern? oder public?)
ufw allow 8000/tcp    # ChromaDB (nur localhost oder VPN?)
ufw allow 443/tcp     # HTTPS
ufw enable
```

19. **WhatsApp-Auth via HMAC**:
```python
# Webhook-Validierung
import hmac, hashlib
SECRET = os.getenv("WHATSAPP_WEBHOOK_SECRET")
def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

20. **Nexos-Fallback-Logik**:
```python
# ai/providers.py
PROVIDERS = ["gemini", "anthropic", "nexos"]
def get_completion(prompt: str):
    for provider in PROVIDERS:
        try:
            return call_provider(provider, prompt)
        except RateLimitError:
            continue
    raise AllProvidersFailedError()
```

21. **Log-Rotation via logrotate**:
```
# /etc/logrotate.d/atlas
/var/log/atlas/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
}
```

22. **ChromaDB mit BasicAuth**:
```python
# chroma_client.py
import chromadb
from chromadb.config import Settings

client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=8000,
    settings=Settings(
        chroma_client_auth_provider="basic",
        chroma_client_auth_credentials="user:pass"
    )
)
```

---

## 4. Fehlende/veraltete Referenzen

23. **Kein Link zu go2rtc-Dokumentation**: 
    - `driver/go2rtc_win64` wird genannt, aber keine Version, Download-Link oder Config-Beispiel

24. **Fehlende OpenClaw-Docs**:
    - Kein Link zu offizieller OpenClaw-Gateway-API-Spec
    - Welche Endpoints? Wie sieht Request/Response aus?

25. **Anthropic-Modellname unklar**:
    - "Claude Sonnet 4.5" existiert nicht (Stand 2024: Claude 3.5 Sonnet)
    - Vermutlich gemeint: `claude-3-5-sonnet-20241022`

26. **Gemini-Tier-Definition fehlt**:
    - "Pro-Tier nur" – aber Gemini API hat Free/Pro/Enterprise-Tiers mit unterschiedlichen Limits
    - Rate-Limits nicht dokumentiert

27. **Hostinger-VPS-Spezifikation fehlt**:
    - Keine RAM/CPU/Disk-Anforderungen
    - Ubuntu? Debian? CentOS?

28. **Kein Verweis auf HA-Konfiguration**:
    - "rest_command → ATLAS FastAPI" – aber kein Beispiel-YAML für HA

---

## 5. Sonnet- und Nexos-Setup (explizit)

### Anthropic/Claude-Sonnet

29. **Modellname korrigieren**:
    - Statt "Claude Sonnet 4.5" → `claude-3-5-sonnet-20241022` (oder neueste Version)

30. **API-Key-Verwaltung**:
    - `ANTHROPIC_API_KEY` in OpenClaw-Admin `.env` → wird zu `ANTHROPIC_API_KEY` in Container-ENV
    - **Fehlende Validierung**: Kein Startup-Check, ob Key gültig ist

31. **Rate-Limits**:
    - Anthropic: 5 req/min (Tier 1), 50 req/min (Tier 2)
    - Kein Retry-Mechanismus dokumentiert

32. **Kosten-Tracking**:
    - Sonnet 3.5: $3/MTok Input, $15/MTok Output
    - Keine Budget-Alerts oder Usage-Logging erwähnt

33. **Fallback bei Sonnet-Ausfall**:
    - Wenn `ANTHROPIC_API_KEY` fehlt/ungültig → System sollte auf Gemini fallback, nicht crashen

### Nexos-Einbindung

34. **Nexos-Guthaben-Prüfung fehlt**:
    - "Guthaben nutzbar" – aber kein Code für Balance-Check vor Request

35. **Nexos-Modell-IDs undokumentiert**:
    - Welche Modelle sind verfügbar? (z. B. `nexos-1`, `nexos-turbo`?)
    - Rate-Limits? Context-Window?

36. **Nexos-Request-Format**:
```python
# Beispiel fehlt – sollte ergänzt werden:
def call_nexos(prompt: str) -> str:
    api_key = os.getenv("NEXOS_API_KEY")
    if not api_key:
        raise ValueError("NEXOS_API_KEY nicht gesetzt")
    response = requests.post(
        "https://api.nexos.ai/v1/completions",  # Beispiel-URL
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "nexos-1", "prompt": prompt, "max_tokens": 1000}
    )
    response.raise_for_status()
    return response.json()["text"]
```

37. **Nexos-Fehlerbehandlung**:
    - 402 Payment Required → Guthaben leer
    - 429 Rate Limit → Retry mit Backoff
    - 500 Server Error → Fallback zu anderem Provider

38. **Nexos-Logging**:
    - Keine Erwähnung von Request-Logs (für Debugging/Billing)

---

## Zusammenfassung

**Kritisch (sofort beheben):**
- Backup-Skript implementieren (1)
- OpenClaw-Isolation verstärken (9)
- HTTPS/TLS einrichten (11)
- ChromaDB-Auth aktivieren (14)
- Anthropic-Modellname korrigieren (29)

**Wichtig (vor Go-Live):**
- WhatsApp-Auth (4, 19)
- Log-Rotation (8, 21)
- Nexos-Integration spezifizieren (35–38)
- Firewall härten (18)

**Nice-to-Have (Dokumentation):**
- Links zu OpenClaw/go2rtc (23, 24)
- HA-Config-Beispiel (28)
- VPS-Anforderungen (27)

---

**Token-Nutzung:** ~1.800 / 200.000  
**Review abgeschlossen.**
