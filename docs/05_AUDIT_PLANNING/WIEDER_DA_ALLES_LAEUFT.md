<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Wenn du wieder da bist – alles läuft

Kurz-Checkliste, damit MTHO, Brain, Sehen/Hören/Sprechen und Proof durchlaufen.

---

## Ablauf: Wer triggert was?

**Nicht du vor jeder WhatsApp.** Der Ablauf ist:

1. **Einmal** MTHO starten (z.B. wenn du an den Rechner gehst oder den Tag beginnst) → `START_OMEGA_COCKPIT.bat` oder `batch_launcher/START_BACKEND_SERVICES.bat`. Danach läuft das Backend (Port 8000).
2. **Ab dann** ist **die eingehende Nachricht** der Trigger: Du schickst eine WhatsApp mit @Atlas → HA feuert Event → rest_command ruft MTHO auf → MTHO antwortet. Du startest nichts mehr „vor“ der Nachricht.
3. Optional: **Autostart** (siehe unten), dann ist MTHO bereit sobald der Rechner (4D_RESONATOR (MTHO_CORE)) an ist – du trittst gar nicht als Trigger auf.

---

## 1. .env prüfen (einmalig)

In `c:\MTHO_CORE\.env` sollten gesetzt sein:

| Variable | Zweck |
|----------|--------|
| `OPENCLAW_ADMIN_VPS_HOST`, `OPENCLAW_GATEWAY_TOKEN` | OMEGA_ATTRACTOR erreichbar |
| `HASS_URL`, `HASS_TOKEN` | HA + WhatsApp, Snapshot-URLs |
| `WHATSAPP_TARGET_ID` | Zielnummer für TTS/WhatsApp |
| `ELEVENLABS_API_KEY` | TTS |
| `SCOUT_MX_SNAPSHOT_URL` | **MX am Scout** (z.B. `https://192.168.178.54:8123/api/camera_proxy/camera.scout_mx`) – nur nötig wenn du die Scout-MX-Kamera nutzen willst |
| `CAMERA_SNAPSHOT_URL` | Tapo/Balkon (Fallback Sehen), optional |
| `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` | Für OpenClaw Brain (andere Modelle) |

---

## 2. Dienste starten (Reihenfolge)

### Option A: Ein Klick – alles (MX am PC + Backend + UIs)

```bat
START_OMEGA_COCKPIT.bat
```

Startet nacheinander: **MX-Snapshot-Server** (Port 8555, Brio am PC) und dann **batch_launcher/START_BACKEND_SERVICES.bat** (Backend :8000, Voice-Info :8502). Damit läuft „MTHO sieht“ (Brio) und die lokalen Dienste.

### Option B: Nur MTHO-Dienste (ohne Snapshot-Server)

```bat
batch_launcher/START_BACKEND_SERVICES.bat
```

Wenn du **Scout-MX** oder **Tapo** über `.env` nutzt, reicht das. Für **Brio am PC** zusätzlich Snapshot-Server starten (siehe Option A oder unten).

### MX am PC (Brio) einzeln

```bat
python -m src.scripts.camera_snapshot_server
```

In eigenem Fenster (Port 8555). Nur nötig, wenn du Brio am PC nutzt und **nicht** START_OMEGA_COCKPIT.bat gestartet hast.

### OMEGA_ATTRACTOR (VPS)

Läuft auf dem VPS (Hostinger). Kein lokaler Start nötig. Wenn Config-Probleme oder „nur Gemini 2.5“:

```bat
python -m src.scripts.deploy_openclaw_config_vps
python -m src.scripts.openclaw_doctor_vps
```

---

## 3. Beweis: Alles funktioniert

```bat
cd c:\MTHO_CORE
python -m src.scripts.proof_hoert_sieht_spricht
```

- Report: `data\proof_hoert_sieht_spricht_report.txt`
- WAV (Hören): `media\proof_voice_<timestamp>.wav`
- Snapshot (Sehen): `data\mx_test\proof_mx_*.jpg`
- TTS (Sprechen): `media\proof_tts.mp3` + optional WhatsApp

Exit-Code 0 = alles OK.

---

## 4. Optional: Autonomer Loop

Wenn Events aus `data\events\` automatisch an den Brain und TTS/HA sollen:

```bat
python -m src.services.autonomous_loop
```

In eigenem Fenster laufen lassen.

---

## 5. Schnell-Referenz

| Was | Befehl / Datei |
|-----|------------------|
| **Alles auf einmal** (MX + Backend + UIs) | `START_OMEGA_COCKPIT.bat` |
| Nur MTHO-Dienste | `batch_launcher/START_BACKEND_SERVICES.bat` |
| MX am PC (Brio) einzeln | `python -m src.scripts.camera_snapshot_server` |
| Proof (Hören/Sehen/Sprechen) | `python -m src.scripts.proof_hoert_sieht_spricht` |
| OC Config deployen | `python -m src.scripts.deploy_openclaw_config_vps` |
| OC Config prüfen | `python -m src.scripts.openclaw_doctor_vps` |
| Kern-Context | `docs\05_AUDIT_PLANNING\MTHO_KERN_CONTEXT.md` |
| Status Hören/Sehen/Sprechen | `docs\05_AUDIT_PLANNING\MTHO_HOERT_SIEHT_SPRICHT_STATUS.md` |

**Wenn du wieder da bist:** .env prüfen → einmal `START_OMEGA_COCKPIT.bat` (oder `batch_launcher/START_BACKEND_SERVICES.bat`) → danach triggert jede eingehende @Atlas-WhatsApp die Antwort. Optional: Autostart einrichten, dann musst du gar nicht manuell starten.

---

## 6. Optional: Autostart (damit du nicht der Trigger bist)

Damit das MTHO-Backend beim Anmelden/Start von Windows (4D_RESONATOR (MTHO_CORE)) startet und WhatsApp sofort funktioniert:

- **Startordner:** `Win+R` → `shell:startup` → Verknüpfung zu `batch_launcher/START_BACKEND_SERVICES.bat` (oder `START_OMEGA_COCKPIT.bat`) ablegen. Dann starten die Dienste beim Login.
- **Oder Taskplaner:** Aufgabe „Beim Anmelden“ erstellen, Aktion: `C:\MTHO_CORE\batch_launcher/START_BACKEND_SERVICES.bat` (Arbeitsverzeichnis: `C:\MTHO_CORE`).

Danach ist MTHO bereit, sobald der Rechner läuft – die eingehende Nachricht triggert die Kette.
