<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Nexos-Einbindung im CORE/OpenClaw-Kontext

**Zweck:** Nexos als LLM-Provider unter unserer Kontrolle dokumentieren; Modell-IDs, Konfiguration und Fehlerbehandlung. Datenquelle für Konfiguration = **bestehende (defekte) OpenClaw-Docker-Instanz** (dort sind WhatsApp, Nexos und weitere Provider bereits eingetragen).

---

## 1. Datenquelle: bestehende OpenClaw-Instanz

- **Wo:** Aktuelle Hostinger-OpenClaw-Instanz (Container z. B. `openclaw-ntw5-openclaw-1`), Config unter `/data/.openclaw/openclaw.json` bzw. auf dem Host unter dem zugehörigen Volume.
- **Was übernehmen:** Nexos-Provider-Block (`models.providers.nexos`: baseUrl, apiKey, models mit IDs), WhatsApp-Channel-Einstellungen, weitere bereits genutzte Kanäle/Provider – als Referenz für die **neue OpenClaw-Admin-Instanz** und für CORE (Nexos-Modul).
- **Wie:** Per SSH/`docker exec` die `openclaw.json` vom laufenden Container auslesen; daraus Nexos-baseUrl, Modell-IDs und Struktur in diese Doku und ins Nexos-Modul übernehmen. Kein manuelles Erfinden von IDs.

---

## 2. Nexos-Provider (OpenClaw)

- **baseUrl:** `https://api.nexos.ai/v1` (typisch; aus bestehender Config bestätigen).
- **API-Key:** Aus CORE `.env` als `NEXOS_API_KEY`; in OpenClaw-Admin als Umgebungsvariable an den Container übergeben und in der Config referenziert (z. B. `$NEXOS_API_KEY` oder Platzhalter, den OpenClaw durch ENV ersetzt).
- **Modelle:** Nur 3.x/Pro-Modelle; konkrete Modell-IDs (z. B. für Nexos GPT 4.1, Gemini 3.x über Nexos) aus der bestehenden `openclaw.json` übernehmen und hier auflisten (z. B. `nexos/a5a1be3e-...` etc.).
- **Guthaben:** Nexos-Guthaben wird über den eigenen Account/Key genutzt; keine zusätzliche Dokumentation von „Balance-Check“ erforderlich, solange Fehlerbehandlung (402, 429) im Modul vorgesehen ist.

---

## 3. Nexos-Modul (CORE)

- **Ort:** Modul unter `src/network/` oder `src/ai/` (z. B. `nexos_client.py` oder in bestehendem Provider-Layer).
- **Inhalt:** Aufruf der Nexos-API (baseUrl + Endpoint aus bestehender OpenClaw-Config), Nutzung von `NEXOS_API_KEY` aus der Umgebung, Modell-IDs aus dieser Doku bzw. aus der übernommenen Config.
- **Fehlerbehandlung:** 402 (Payment Required) → Hinweis „Guthaben leer“; 429 (Rate Limit) → Retry mit Backoff; 5xx → Fallback auf anderen Provider (Gemini/Anthropic), falls vorgesehen. Optional: Logging für Billing/Debug.
- **Doku:** Diese Datei; Modell-IDs und ggf. Rate-Limits nach Übernahme aus der bestehenden OpenClaw-Instanz hier ergänzen.

---

## 4. Offene Punkte (nach Übernahme)

- Rate-Limits (Nexos-seitig) in Doku eintragen, sobald aus Config/Docs bekannt.
- Optional: Balance-Check vor Request (wenn Nexos-API das anbietet).
- Log-Rotation und Request-Logs für Nexos-Aufrufe, falls gewünscht, in Betriebsdoku festhalten.

---

## Referenzen

- [OPENCLAW_ADMIN_ARCHITEKTUR.md](OPENCLAW_ADMIN_ARCHITEKTUR.md)
- [PROJEKT_ANNAHMEN_UND_KORREKTUREN.md](../05_AUDIT_PLANNING/PROJEKT_ANNAHMEN_UND_KORREKTUREN.md)
- Bestehende OpenClaw-Config auf VPS: z. B. `python -m src.scripts.check_openclaw_config_vps` bzw. Container `openclaw-ntw5-openclaw-1`, Pfad `/data/.openclaw/openclaw.json`.
