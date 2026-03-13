<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Offene Punkte aus Audit

Dinge, die sich nicht allein aus dem Kontext ableiten lassen oder an manchen Stellen fehlen/abstrakt sind – zur Klärung oder späteren Umsetzung.

---

## Sicherheit

| Punkt | Beschreibung | Was fehlt / zu klären |
|-------|--------------|------------------------|
| **WhatsApp HMAC** | Meta verlangt Signaturprüfung (HMAC-SHA256) für Webhook-Callbacks. | Konkrete Webhook-URL, Meta App Secret; Implementierung in `whatsapp_webhook.py` (Payload prüfen). |
| **TLS für FastAPI-Webhook** | WhatsApp/Webhooks erfordern HTTPS. | Zertifikat (Let's Encrypt, NGROK, oder Reverse-Proxy auf VPS); Doku, wo TLS terminiert wird. |
| **ChromaDB bereits öffentlich** | Falls der VPS schon mit alter Chroma-Bindung läuft (`-p 8000:8000`): Port ist von außen erreichbar. | Auf bestehenden VPS: Container neu erstellen mit `-p 127.0.0.1:8000:8000` (Daten im Volume bleiben); Zugriff dann nur per SSH-Tunnel. |

---

## Architektur / Konsistenz

| Punkt | Beschreibung |
|-------|--------------|
| **Backup-Ziele** | Abgleich erledigt: Einziges Ziel = Hostinger, siehe [BACKUP_PLAN_FINAL.md](../03_INFRASTRUCTURE/BACKUP_PLAN_FINAL.md). |
| **WhatsApp-Webhook-Routing** | Vollständiger Pfad: Nachricht → HA (Addon) → rest_command → CORE FastAPI `/webhook/whatsapp`. Siehe [WHATSAPP_E2E_HA_SETUP.md](../03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md). |
| **ChromaDB Auth** | ChromaDB-Client (`chroma_client.py`) hat keine Auth-Dokumentation; bei Remote-Betrieb Zugriff nur über SSH-Tunnel (kein separater Auth-Layer). |

---

## Vaultwarden (Scout) – Secrets & Verschlüsselung

**Stand:** Auf dem Scout läuft Vaultwarden; du nutzt es bereits (z. B. Passwörter aus Chrome). Es erscheint sinnvoll, **Vaultwarden als zentrale Quelle für Secrets** zu nutzen.

**Zu klären / umsetzen:**

- **BACKUP_ENCRYPTION_KEY:** Den Schlüssel für die Backup-Verschlüsselung (.env im Backup) in Vaultwarden ablegen; bei Bedarf manuell in .env eintragen oder (später) per Vaultwarden-API/CLI in die Umgebung holen, damit `daily_backup.py` .env verschlüsselt ins Archiv packen kann.
- **Weitere Secrets (API-Keys, Tokens):** Mittelfristig können weitere .env-Werte aus Vaultwarden bezogen werden (z. B. GEMINI_API_KEY, OPENCLAW_GATEWAY_TOKEN), um .env schlank und auditierbar zu halten. Dafür ist eine Anbindung (Skript/Startup) noch offen – **offener Punkt**.

Vaultwarden-Entities sind in HA sichtbar (z. B. `binary_sensor.vaultwarden_bitwarden_lauft`); eine technische Integration (API/CLI) für CORE ist noch zu spezifizieren.

---

## UI / Status-Anzeige & Metriken (Kamera, WhatsApp, Kosten)

| Thema | Anforderung | Offen |
|-------|-------------|--------|
| **Kamerastream** | Schalter, Button oder Hinweis: Stream läuft nicht / nicht gestattet / langsam / muss angefordert werden; ggf. Aktion zum Anfordern oder Neustarten. Parallel in AI Studio aufgesetzt. | Anzeige im CORE-CORE-Frontend/Dashboard einplanen; welche Komponente (Stream/Snapshot-Server) meldet Status? |
| **WhatsApp-Webhook** | Anzeige: Welche Teile der Verbindung stehen (HA, rest_command, CORE-API, Webhook), welche fehlen; Hinweis, ob etwas per Script neu angestoßen werden muss. | Welche Status-Checks (Ping HA, API erreichbar, …) und wo anzeigen? |
| **Token-Überwachung / API-Kosten** | Da wir Paid-APIs (Gemini/Anthropic/Nexos) nutzen, muss der Token-Verbrauch bzw. die Kosten überwacht und ins Dashboard geführt werden. | Einbau von Token-Zählern in die API-Requests und eine Dashboard-Ansicht (oder Alert bei Threshold-Überschreitung). |

---

## Optional / mittelfristig

- **healthchecks.io:** Optional in .env als `HEALTHCHECK_URL` – bei Erfolg wird die URL von `daily_backup.py` aufgerufen (Dead-Man’s-Switch bei ausbleibendem Backup).
- **ChromaDB Cold-Backup auf VPS:** Separates Skript auf dem VPS (Container stoppen → Verzeichnis archivieren → starten); optional per Cron. In BACKUP_PLAN_FINAL erwähnt; Skript nicht Teil von CORE-Repo.

---

## Sigma-70 Nachzuegler (langfristig priorisiert)

| ID | Punkt | Prio | Beschreibung |
|----|-------|------|-------------|
| S70-01 | Veto Gate Body-Signierung | MITTEL | X-Veto-Confirm aktuell statischer Secret-Vergleich. Upgrade auf HMAC-SHA256 Body-Signierung. Aendert API-Contract. Umsetzen wenn VETO_HMAC_SECRET produktiv. |
| S70-02 | Vision Daemon async Rewrite | NIEDRIG | core_vision_daemon.py synchroner CV2-Loop. Vollstaendiger async Rewrite. Groesseres Refactoring. |
| S70-03 | Takt-Gate echte Drift-Metrik | HOCH | check_baryonic_limit() bewusst deaktiviert (Tautologie). Braucht echte Telemetrie-Daten. NICHT gegen 0.5 pruefen (Axiom A5). |
