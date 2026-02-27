===== AUDIT (Claude Opus 4.6 – Modell: claude-opus-4-6) =====

# DEV_AGENT_REVIEW_ANMERKUNGEN (Claude Audit)

**Datum:** Review auf Basis der bereitgestellten Dokumentenauszüge
**Scope:** Schnittstellen, Architektur, Sicherheit, Backup-Planung
**Bezug:** Gemini-Vorab-Review wird mitbewertet

---

## 1. Lücken / Widersprüche

**1.1 Backup-Ziel-Divergenz (bestätigt Gemini)**
Dokument 2 nennt als Ziele „lokal + optional S3/GCS". Dokument 3 definiert den VPS explizit als Backup-Ziel (`/var/backups/atlas`, Push von innen). Dokument 4 kennt nur `BACKUP_DIR` und optional `AWS_*`. **Es gibt drei Dokumente mit drei unterschiedlichen Ziel-Definitionen.** → Ein einziges, verbindliches Backup-Routing-Diagramm fehlt.

**1.2 ChromaDB-Standort-Ambiguität**
Dokument 1 erlaubt „Lokal (PersistentClient) *oder* Remote (CHROMA_HOST)". Dokument 3 setzt ChromaDB auf den VPS. Es fehlt eine klare Entscheidung, welcher Modus produktiv gilt. Das hat Folgewirkung auf Latenz (Ollama lokal ↔ Chroma remote), Backup-Scope und Netzwerk-Sicherheit. **Gemini erwähnt die fehlende Chroma-Sicherung korrekt, aber die tiefere Ursache ist die nicht fixierte Deployment-Entscheidung.**

**1.3 WhatsApp-Rückkanal / Webhook-Proxy (bestätigt + erweitert Gemini)**
Die Kette `WhatsApp → HA (Addon) → rest_command → ATLAS FastAPI /webhook/whatsapp` setzt voraus, dass HA von außen erreichbar ist (für den WhatsApp-Cloud-API-Callback) **oder** dass das HA-Addon selbst pollt. Der in Dokument 3 genannte „Webhook-Proxy" auf dem VPS könnte als Eingangstor dienen, ist aber nirgends spezifiziert:
- Kein Reverse-Proxy-/Tunnel-Konzept (Cloudflare Tunnel, WireGuard, Tailscale) dokumentiert.
- Kein Sequenzdiagramm, das den vollständigen Hin- und Rückweg zeigt.
- Die Scout-Handler-Erwähnung in Dokument 4 ist „offen" ohne Abhängigkeiten oder Priorität.

**1.4 Ollama-Platzierung unklar**
Dokument 3 nennt „optional leichtes Ollama" auf dem VPS. Dokument 1 setzt Ollama als Abhängigkeit implizit voraus (Sandbox darf nicht zugreifen). Es fehlt:
- Entscheidung: Ollama lokal, VPS oder beides?
- Ressourcen-Abschätzung für den VPS (Hostinger-RAM für Ollama + Chroma + OpenClaw).
- Fallback-Verhalten, wenn Ollama nicht erreichbar ist.

**1.5 Go2RTC / Kamera-Integration → keine Fehlerbehandlung**
Dokument 1 listet mehrere Kamera-Skripte (Tapo, Brio, Snapshot-Server). Es fehlt:
- Welche Skripte auf welchem Host laufen (PC vs. Scout).
- Netzwerk-Voraussetzungen (Multicast, RTSP-Ports, Firewall-Regeln lokal).
- Fehlerfall: Was passiert, wenn go2rtc oder die Kamera offline ist? Kein Health-Check definiert.

**1.6 Fehlende Abhängigkeitsgraphen zwischen Tasks**
Dokument 4 listet Tasks als flache Liste. Es fehlen Abhängigkeiten: z. B. „VPS-Setup muss vor Chroma-Deployment abgeschlossen sein", „Backup-Skript benötigt funktionierenden VPS-Zugang". Ohne Abhängigkeitsgraph ist die Reihenfolge unklar.

---

## 2. Sicherheitshinweise

**2.1 ChromaDB-Exposition (bestätigt Gemini, Severity: KRITISCH)**
Port 8000 offen ins Internet ist nicht akzeptabel. ChromaDB hat kein eingebautes Auth-System in der Standardkonfiguration. **Maßnahmen (Priorität 1):**
- Port 8000 nur an `127.0.0.1` binden.
- Zugriff ausschließlich über WireGuard/Tailscale-Tunnel oder Reverse Proxy mit Token-Auth.
- Alternativ: ChromaDB nur lokal betreiben (PersistentClient), dann entfällt das Problem vollständig.

**2.2 Secrets in Backups (bestätigt Gemini, Severity: HOCH)**
`.env` enthält API-Keys, DB-Credentials, Tokens. Ergänzung zu Geminis Vorschlag:
- `Fernet` ist akzeptabel für symmetrische Verschlüsselung, aber der **Schlüssel selbst darf nicht im Backup liegen**.
- Besser: `age` (https://github.com/FiloSottile/age) oder `gpg` – Schlüssel bleibt auf dem Quell-Host, Public Key reicht zum Verschlüsseln.
- **Vor dem ersten externen Upload muss Verschlüsselung implementiert sein – nicht „optional".**

**2.3 OpenClaw-Sandbox-Härtung (ergänzt Gemini)**
Geminis Vorschlag `read_only: true` + Ressourcenlimits ist korrekt. Zusätzlich:
```yaml
# docker-compose Snippet
services:
  openclaw:
    read_only: true
    tmpfs:
      - /tmp
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    networks:
      - openclaw_net  # isoliert, kein Zugriff auf chroma_net
```
- `cap_drop: ALL` + `no-new-privileges` fehlen in allen Dokumenten.
- Logging: Container-Logs sollten nach außen gestreamt werden (Docker log driver → Datei oder Loki), damit bei einem Sandbox-Ausbruch Audit-Trail existiert.

**2.4 SSH-Zugang zum VPS**
Dokument 3 erwähnt SSH (Port 22), aber:
- Keine Erwähnung von Key-Only-Auth (PasswordAuthentication no).
- Kein Fail2Ban oder Rate-Limiting.
- Kein separater Deploy-User (alles scheint als root zu laufen → `/root` wird erwähnt).
- **Empfehlung:** Dedizierter User `atlas-deploy`, SSH nur per Key, Port ≠ 22, Fail2Ban aktiv.

**2.5 Token-Verwaltung für OpenClaw-Gateway**
Dokument 3: „ATLAS nutzt Token von außen". Es fehlt:
- Wo wird der Token gespeichert? (`.env`? Vault?)
- Rotation-Strategie.
- Was passiert bei Token-Leak? Revocation-Prozess?

**2.6 Kein TLS-Konzept**
Dokument 3 erwähnt Port 80/443, aber kein konkretes TLS-Setup:
- Kein Let's Encrypt / Certbot erwähnt.
- Kein Reverse-Proxy (Caddy/Nginx/Traefik) für automatisches TLS.
- Interne Kommunikation (Chroma, Ollama, OpenClaw) unverschlüsselt dokumentiert.

---

## 3. Verbesserungsvorschläge

**3.1 Backup-Architektur konsolidieren**
Einen einzigen `BACKUP_ARCHITECTURE.md` erstellen mit:

| Quelle | Daten | Ziel Primär | Ziel Sekundär | Transport | Verschlüsselung |
|---|---|---|---|---|---|
| Lokaler PC | Code, .env, SQLite | Lokales NAS / Ordner | S3 (verschlüsselt) | Lokal / boto3 | age/gpg |
| VPS | ChromaDB-Persist, OpenClaw-Config | /var/backups/atlas | S3 | Lokales Skript auf VPS | age/gpg |

**3.2 Health-Check-Endpunkte**
Für jede Komponente einen `/health`-Endpoint definieren:
- ATLAS FastAPI: bereits vorhanden?
- ChromaDB: `GET /api/v1/heartbeat`
- Ollama: `GET /api/tags`
- OpenClaw: Prüfen, ob Health-Endpoint existiert
- Go2RTC: `GET /api/streams`

→ Zentrales Monitoring-Skript, das alle Endpoints pollt und bei Ausfall alarmiert.

**3.3 Monitoring-Kanal (ergänzt Gemini)**
Geminis Vorschlag (Discord/Telegram statt SMTP) ist pragmatisch richtig. Konkreter Vorschlag:
```python
# utils/notify.py
import httpx, os

async def notify(message: str):
    """Sendet an konfigurierten Kanal. Failover: Log."""
    url = os.getenv("NOTIFY_WEBHOOK_URL")  # Discord/Telegram/Slack
    if url:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json={"content": message}, timeout=10)
        except Exception:
            pass  # Fallback: nur Log
    logging.warning(f"[NOTIFY] {message}")
```

**3.4 Restore-Prozedur dokumentieren**
Dokument 2 nennt „monatlicher Restore-Test", aber es fehlt eine konkrete Restore-Anleitung:
- Schritt-für-Schritt: Archiv entschlüsseln → entpacken → DB wiederherstellen → Config prüfen → Smoke-Test.
- Erwartete Recovery Time Objective (RTO) und Recovery Point Objective (RPO).
- Verantwortlichkeit (wer führt den Test durch?).

**3.5 Docker-Compose als Single Source of Truth**
Die VPS-Dienste (OpenClaw, ChromaDB, ggf. Ollama, Reverse Proxy) sollten in einem einzigen `docker-compose.prod.yml` definiert sein, das:
- Netzwerk-Isolation deklarativ abbildet.
- Alle Ports, Mounts, Limits enthält.
- Versioniert im Repo liegt.
Aktuell verteilt sich die Information über drei Dokumente + ein Setup-Skript.

**3.6 Environment-Validierung beim Start**
ATLAS sollte beim Boot alle erforderlichen Env-Variablen prüfen und mit klarer Fehlermeldung abbrechen, wenn etwas fehlt:
```python
REQUIRED_ENV = ["GEMINI_API_KEY", "CHROMA_HOST", "BACKUP_DIR", ...]
missing = [v for v in REQUIRED_ENV if not os.getenv(v)]
if missing:
    raise SystemExit(f"Fehlende Env-Variablen: {', '.join(missing)}")
```

---

## 4. Fehlende / veraltete Referenzen

**4.1 Gemini-Modellbezeichnung (bestätigt Gemini, Korrektur nötig)**
„3.1 Pro Standard" existiert nicht in Googles Nomenklatur. Aktuell gültig (Stand Mitte 2025): `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`. **Auch Geminis eigene Korrektur auf `gemini-1.5-pro` ist inzwischen veraltet.** → Modellbezeichnung im Dokument auf den tatsächlich genutzten Modellnamen aktualisieren und als Variable (`GEMINI_MODEL`) in `.env` auslagern.

**4.2 „Nano Banana Pro" – nicht verifizierbar**
Dokument 1 nennt „Nano Banana Pro nur für Generierung". Dieser Modellname ist in keiner öffentlichen Google-Dokumentation zu finden. → Klären, ob es sich um einen internen Alias, ein Community-Modell oder einen Irrtum handelt. Dokumentieren oder entfernen.

**4.3 `daily_backup.py` – referenziert, nicht existent**
Wird in Dokument 1, 2 und 4 referenziert, Status in Dokument 4 explizit „offen". Das Skript ist die zentrale Backup-Komponente. **Solange es nicht existiert, gibt es kein funktionierendes Backup.** → Höchste Priorität.

**4.4 `setup_vps_hostinger.py` – Wartbarkeit unklar**
Ein Python-Skript für VPS-Provisioning ist fragil. Besser: Ansible-Playbook oder zumindest ein dokumentiertes Shell-Skript mit Idempotenz. Falls Python beibehalten wird, fehlen Fehlerbehandlung und Idempotenz-Garantien in der Dokumentation.

**4.5 Fehlende `requirements.txt`-Einträge**
Aus den Dokumenten ergeben sich Abhängigkeiten, die dokumentiert sein müssen:
- `boto3` (S3-Upload)
- `cryptography` oder `age`-Wrapper (Backup-Verschlüsselung)
- `httpx` (falls async Notifications)
- `chromadb` (Client)
- ChromaDB-Server-Version auf dem VPS (Docker-Image-Tag fehlt)

**4.6 Kein Versionspinning**
Keine einzige Docker-Image-Version wird in den Dokumenten fixiert (ChromaDB: `latest`? `0.5.x`?). Kein Python-Dependency-Pinning erwähnt. → Reproduzierbarkeit gefährdet.

---

## 5. Bewertung der Gemini-Anmerkungen

| Gemini-Punkt | Bewertung | Kommentar |
|---|---|---|
| Backup-Ziele & Routing | ✅ Korrekt | Gemini erkennt die Divergenz. Die Ursache (drei Dokumente, keine Single Source) hätte stärker betont werden können. |
| ChromaDB-Sicherung | ✅ Korrekt | Guter Punkt. Ergänzung: Das Problem wurzelt in der unklaren Deployment-Entscheidung (lokal vs. remote). |
| WhatsApp-Routing | ✅ Korrekt | Gemini benennt die Lücke richtig. Es fehlt aber die Erwähnung, dass auch der eingehende Webhook-Pfad (Meta → HA) eine öffentliche URL braucht. |
| ChromaDB Port-Exposition | ✅ Korrekt, Kritisch | Maßnahmen sind richtig priorisiert. |
| Secrets im Backup | ✅ Korrekt | Geminis Fernet-Vorschlag funktioniert, aber symmetrische Schlüsselverwaltung ist ein Risiko. `age`/`gpg` wäre robuster. |
| OpenClaw Sandbox | ✅ Korrekt | `read_only` + Limits sind gut. `cap_drop: ALL` und `no-new-privileges` fehlten bei Gemini. |
| Monitoring Discord/Telegram | ✅ Pragmatisch richtig | Gute Empfehlung. |
| Dynamische Pfade | ✅ Korrekt | Kleiner aber wichtiger Punkt. |
| Gemini-Modellname | ⚠️ Teilweise korrekt | Gemini korrigiert auf `1.5-pro/flash`, was selbst bereits veraltet ist. Aktuell: `2.5-pro/flash` bzw. `2.0-flash`. |
| boto3 in requirements | ✅ Korrekt | Valider Punkt. |

**Gesamtbewertung Gemini-Review:** Solide Erstanalyse mit korrekten Kernbefunden. Schwächen: (a) Architektur-Entscheidungslücken werden als Dokumentationslücken behandelt statt als Design-Schulden, (b) SSH-Härtung, TLS, Token-Rotation und Container-Hardening wurden nicht adressiert, (c) die eigene Modellnamens-Korrektur war bereits veraltet.

---

## Zusammenfassung – Top-5-Maßnahmen nach Priorität

| # | Maßnahme | Severity | Aufwand |
|---|---|---|---|
| 1 | **ChromaDB-Zugriff absichern** (kein offener Port 8000) | 🔴 Kritisch | Mittel |
| 2 | **`daily_backup.py` implementieren** inkl. Verschlüsselung | 🔴 Kritisch | Mittel |
| 3 | **Deployment-Entscheidungen fixieren** (Chroma lokal/remote, Ollama-Standort) in einem Architecture Decision Record | 🟠 Hoch | Gering |
| 4 | **SSH-Härtung + TLS-Setup** auf VPS | 🟠 Hoch | Gering |
| 5 | **Docker-Compose konsolidieren** als Single Source of Truth für VPS-Dienste | 🟡 Mittel | Mittel |
