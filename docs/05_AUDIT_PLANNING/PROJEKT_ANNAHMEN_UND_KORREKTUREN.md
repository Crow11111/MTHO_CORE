<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Projekt-Annahmen und Korrekturen (nach Dev-Agent-Review)

**Zweck:** Falsche Annahmen aus Reviews korrigieren und verbindliche Vorgaben für das Projekt festhalten.

---

## 1. Gemini-Modelle

- **Standard:** Überall **Gemini 3.1 Pro** – Modell-ID: `gemini-3.1-pro-preview`. Keine Abweichung auf „1.5“; Gemini 1.5 ist **nicht** neuer und wird nicht als Standard genutzt.
- **Fallback:** Vorbeck-Modell = **Gemini 3.0 Preview** (`gemini-3-pro-preview`).
- **Dokumentation:** In allen Docs und Konfigurationen explizit „Gemini 3.1 Pro (preview)“ bzw. `gemini-3.1-pro-preview` verwenden.

---

## 2. Anthropic-Modelle (Claude)

- **Claude Opus 4.6** und **Claude Sonnet 4.6** – beide 4.6. Modell-IDs im Projekt: `claude-opus-4-6`, `claude-sonnet-4-5` / `claude-4-6-sonnet` (je nach API-Stand); in der Doku einheitlich als „Claude Opus 4.6“ und „Claude Sonnet 4.6“ bezeichnen.
- Bei Abweichungen zwischen API-Dokumentation und unseren Bezeichnungen: aktuelle Anthropic-API prüfen und hier bzw. in `dev_agent_claude46.py` / OpenClaw-Config anpassen.

---

## 3. Backup

- **Verschlüsselung:** Backups werden **vorerst ohne** Verschlüsselung umgesetzt; Verschlüsselung kommt später.
- **Ziel:** Primär **VPS** (`/var/backups/core`). „S3 oder beides“ = optional später; Hauptinstanz für Backup-Ziel ist der VPS.
- Backup-Skript und -Ablauf werden separat (z. B. in BACKUP_PLAN_FINAL.md, daily_backup.py) beschrieben.

---

## 4. OpenClaw-Container

- **Anzahl:** Es gibt **2** OpenClaw-Instanzen (Container); vorübergehend **3**. Jeder Container = eine OpenClaw-Instanz (Admin vs. Spine vs. ggf. dritte).
- **Deployment:** Admin = **Docker Compose** (`docker/openclaw-admin/`). Spine und ggf. dritte Instanz können weiterhin einzeln oder per Compose laufen – einheitlich in der Doku als „Container pro Instanz“ beschreiben.
- **Sandbox:** Die vom Dev-Agent geforderten Sandbox-Maßnahmen (eigenes Netzwerk, kein Host-Netzwerk, keine sensiblen Mounts) werden so umgesetzt und dokumentiert.

---

## 5. Gateway-Token

- **Handling:** Klar definiert und dokumentiert in [OPENCLAW_GATEWAY_TOKEN.md](../02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md) (Speicherort, Rotation, Verwendung in CORE/OpenClaw).

---

## 6. Nexos / WhatsApp / bestehende OpenClaw-Instanz

- **Datenquelle:** Nexos-Konfiguration, WhatsApp-Setup und alle anderen bereits eingebauten Daten werden **von der bestehenden (defekten) OpenClaw-Docker-Instanz** übernommen (aus dem laufenden Container bzw. dessen Config extrahieren).
- **Nexos:** Modul und Doku siehe [NEXOS_EINBINDUNG.md](../02_ARCHITECTURE/NEXOS_EINBINDUNG.md); technische Details (Modell-IDs, baseUrl) aus der bestehenden OpenClaw-Config übernehmen.

---

## 7. ChromaDB

- **Port:** Auf dem VPS ist ChromaDB bereits an **127.0.0.1:8000** gebunden (`setup_vps_hostinger.py`: `-p 127.0.0.1:8000:8000`). Kein öffentlicher Zugriff auf Port 8000; Zugriff von außen nur per SSH-Tunnel.
- Ob ein anderer Port genutzt wird, ist in der Doku zu prüfen; aktuell bleibt 8000 an localhost.

---

## 8. WhatsApp-Flow

- **Stand:** WhatsApp-Flow wird **erstmal so übernommen**, wie er bis jetzt umgesetzt ist (keine Änderung am bestehenden Ablauf für die Korrekturrunde).

---

## 9. SSH und Secrets

- **SSH:** Nur Zugriff klären; Umgang mit Secrets (Keys, Tokens) klären, **härten, dokumentieren und umsetzen** (z. B. Key-Only, keine Root-Passwörter in Klartext, wo welche .env liegt).
- Konkrete Maßnahmen und Checklisten in VPS- und Sicherheitsdoku übernehmen.

---

## 10. Nexos-Modul und Doku

- **Modul:** Nexos-Anbindung als Modul aufsetzen (z. B. unter `src/network/` oder `src/ai/`); Konfiguration und Modell-IDs aus der bestehenden OpenClaw-Instanz übernehmen.
- **Doku:** [NEXOS_EINBINDUNG.md](../02_ARCHITECTURE/NEXOS_EINBINDUNG.md) – Modell-IDs, Rate-Limits, Fehlerbehandlung, Abnahme der Daten aus der bestehenden OpenClaw-Config.

---

## Referenzen

- [OPENCLAW_ADMIN_ARCHITEKTUR.md](../02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md)
- [OPENCLAW_GATEWAY_TOKEN.md](../02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md)
- [NEXOS_EINBINDUNG.md](../02_ARCHITECTURE/NEXOS_EINBINDUNG.md)
- [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](../03_INFRASTRUCTURE/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md)
- [DEV_AGENT_REVIEW_ANMERKUNGEN.md](DEV_AGENT_REVIEW_ANMERKUNGEN.md)
