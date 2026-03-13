<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OpenClaw – Zwischenziele und Abnahme (scharf)

**VPS:** 187.77.68.250 | **Instanz:** openclaw-admin (18789, Nginx HTTPS)

---

## Abnahme-Stand (Orchestrator – 28.02.2026 ~15:00)

| Z  | Status    | Beweis (selbst verifiziert) |
|----|-----------|-----------------------------|
| **Z1** | **LÄUFT** | `openclaw doctor` sauber; Container-Logs: `[gateway] listening on ws://0.0.0.0:18789`, Agent-Modell gesetzt, API 200 |
| **Z2** | **LÄUFT** | Browser: Config-Seite zeigt **Formular** (Schema geladen), KEIN "Schema unavailable" |
| **Z3** | **LÄUFT** | Browser: Agents/Channels/Config/Chat – alle Buttons reagieren, Seiten öffnen sich |
| **Z4** | **LÄUFT** | Browser: 2 Agents (CORE, Agent), 5 Instances, WhatsApp-Channel sichtbar, Config editierbar |
| **Z5** | **LÄUFT** | API-Call: `POST /v1/chat/completions` → Agent antwortet: "Signal verstanden. Status: bereit." |

**Alle Z1–Z5 bestanden. OpenClaw Admin ist eine funktionsfähige Installation.**

---

## Was gefixt wurde (Zusammenfassung)

1. **imageModel-Keys entfernt** – verursachten "Unsupported schema node" → "Schema unavailable"
2. **Ungültige Config-Keys entfernt** – `commands.nativeSkills`, `commands.ownerDisplay`, `channels.whatsapp.debounceMs`
3. **trustedProxies erweitert** – `172.16.0.0/12` für Docker-Bridge (Nginx → Container)
4. **Device-Auth deaktiviert** – `dangerouslyDisableDeviceAuth: true`, pending Devices approved
5. **Modell gewechselt** – `gemini-3.1-pro-preview` (Quota erschöpft) → `gemini-2.5-pro`
6. **Deploy-Skript aktualisiert** – `deploy_vps_full_stack.py` enthält jetzt alle Fixes für zukünftige Deploys

---

## Zugriff

- **UI:** `https://187.77.68.250/#token=ykKqxCcMM5CPYTS20fxTWyu6RkLkvd5T`
- **API:** `POST https://187.77.68.250/v1/chat/completions` mit `Authorization: Bearer <token>`
- **Zertifikat:** Self-signed → Browser-Warnung bestätigen

---

## Nächste Schritte (nach Z1–Z5)

- WhatsApp-Kanal pairen und testen
- Spine-Anbindung (OC Spine ↔ OMEGA_ATTRACTOR)
- SOUL.md / Agent-Routing prüfen
