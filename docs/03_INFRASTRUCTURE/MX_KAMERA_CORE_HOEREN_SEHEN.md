<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# MX-Kamera (Logitech Brio) – CORE hören und sehen

Kurzanleitung: So nutzt CORE die MX/Brio am 4D_RESONATOR (CORE)-PC zum **Sehen** und (optional) zum **Hören**.  
**Scout-MX:** USB-MX am Scout (Raspi/HA) → Proof „Sehen“ mit Quelle `scout_mx` (siehe Abschnitt „Scout-MX einbinden“).

---

## Scout-MX einbinden (Kamera am Scout/Raspi/HA)

**Stand:** `SCOUT_MX_SNAPSHOT_URL` zeigt auf `camera.scout_mx`. Sobald diese Kamera in HA existiert, läuft der Proof „Sehen“ mit Quelle scout_mx.

Damit Proof „Sehen“ mit Quelle **scout_mx** funktioniert:

1. **HA-Seite:** USB-MX am Scout in Home Assistant sichtbar machen.
   - **Typisch:** Generic Camera oder **FFmpeg**-Integration mit Eingabe `/dev/video0` (HA OS erkennt UVC-Kamera).
   - **Entity-ID:** z.B. `camera.scout_mx` (frei wählbar; Default in CORE: `camera.scout_mx`).
   - **Anlegen:** YAML (`configuration.yaml`) oder **Einstellungen → Geräte & Dienste → Kamera hinzufügen** (FFmpeg/Generic Camera).
2. **CORE-Seite:** `SCOUT_MX_SNAPSHOT_URL` setzen = `HASS_URL` + `/api/camera_proxy/<entity_id>`.
   - **Empfohlen:** `python -m src.scripts.setup_scout_mx` (oder `set_scout_mx_snapshot_url`) ausführen. Liest HASS_URL (Fallback HA_URL) und HASS_TOKEN (Fallback HA_TOKEN) aus .env; baut die URL; prüft optional per GET gegen HA, ob die Camera-Entity existiert; schreibt nur die Zeile `SCOUT_MX_SNAPSHOT_URL=…` in .env (bestehende Zeile wird ersetzt, sonst angehängt; keine Löschung anderer .env-Inhalte).
   - **Aufruf:** `python -m src.scripts.setup_scout_mx [--entity camera.scout_mx] [--no-check] [--dry-run]`. Entity-ID auch per Umgebungsvariable `SCOUT_MX_ENTITY_ID`. Mit `--dry-run` wird nur die Zeile ausgegeben (zum manuellen Eintrag).
   - **Manuell:** In `.env` eintragen: `SCOUT_MX_SNAPSHOT_URL=https://<Scout-IP>:8123/api/camera_proxy/camera.scout_mx` (HASS_TOKEN für Proxy-Aufruf setzen).
3. **Proof ausführen:** `python -m src.scripts.proof_hoert_sieht_spricht` → Abschnitt „Sehen“ nutzt Scout-MX, wenn konfiguriert.

Siehe auch: `SCOUT_USB_KAMERA_MIKRO_HA_OS.md`, `.env.template` (SCOUT_MX_SNAPSHOT_URL, HASS_URL, HASS_TOKEN).

---

## Sehen (MX als Bildquelle)

**Reihenfolge der Snapshot-Quellen** (in `go2rtc_client.get_snapshot`):

1. **go2rtc** (localhost:1984, Stream `pc`) – falls go2rtc mit Brio-Stream läuft
2. **MX lokal** – `CAMERA_SNAPSHOT_URL_MX` (Standard: `http://localhost:8555/snapshot.jpg`)
3. **HA/Remote** – `CAMERA_SNAPSHOT_URL` (z.B. `camera.balkon`)

### Option A: On-Demand-Snapshot (Brio nur bei Abruf)

1. In einem Terminal starten:
   ```bash
   python -m src.scripts.camera_snapshot_server
   ```
2. Server läuft auf Port 8555. `go2rtc_client` nutzt automatisch `http://localhost:8555/snapshot.jpg` (Default für `CAMERA_SNAPSHOT_URL_MX`).
3. Kein Eintrag in `.env` nötig, falls Default passt. Sonst:
   ```env
   CAMERA_SNAPSHOT_URL_MX=http://localhost:8555/snapshot.jpg
   ```
4. Gerätename: Wenn die Brio unter Windows als **„Logi Capture“** erscheint, bleibt `CAMERA_DEVICE_NAME` leer oder auf `Logitech BRIO` – der Snapshot-Server versucht nacheinander „Logitech BRIO“, „Logi Capture“, „Logitech BRIO“.

**Tests:**

- `python -m src.scripts.mx_save_images_only` → Bilder in `data/mx_test/`
- `python -m src.scripts.proof_hoert_sieht_spricht` → Abschnitt „Sehen“ nutzt dieselbe Quelle

### Option B: go2rtc mit Brio-Dauerstream

1. `driver/go2rtc_win64/go2rtc.yaml` wie in `go2rtc_brio_example.yaml` (Brio als Stream `pc`) konfigurieren
2. go2rtc starten (z.B. `go2rtc.exe` im Ordner)
3. `CAMERA_SNAPSHOT_URL_MX` leer lassen oder weglassen – dann wird zuerst go2rtc (localhost:1984) verwendet

---

## Hören (Mikrofon am PC)

- **sounddevice** nutzt das Standard-Mikrofon (z.B. Razer Seiren V3 Mini oder „Mikrofon (Logitech BRIO)“).
- Skript: `python -m src.scripts.dreadnought_listen` – Aufnahme → WAV → Event an OMEGA_ATTRACTOR.
- Unter Windows das gewünschte Mikrofon als **Standard-Eingabegerät** setzen, dann braucht CORE keine weitere Konfiguration.

---

## Kurz-Checkliste

| Schritt | Befehl / Aktion |
|--------|------------------|
| MX-Snapshot-Server starten | `python -m src.scripts.camera_snapshot_server` |
| MX-Bilder speichern | `python -m src.scripts.mx_save_images_only` |
| Proof (Sehen + Sprechen + Hören) | `python -m src.scripts.proof_hoert_sieht_spricht` |
| Hören (Aufnahme → Event) | `python -m src.scripts.dreadnought_listen` |
| Scout-MX-URL in .env setzen | `python -m src.scripts.setup_scout_mx` oder `set_scout_mx_snapshot_url` (Optionen: `--entity camera.scout_mx`, `--no-check`, `--dry-run`) |

Siehe auch: `CAMERA_GO2RTC_WINDOWS.md`, `ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md`, `SCOUT_USB_KAMERA_MIKRO_HA_OS.md`.
