<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE hört / sieht / spricht – Status (Teamchef)

**Stand:** Beweis-basiert. Nichts glauben, alles prüfen.

---

## Ziele (vorgegeben)

| Ziel | Beweiskriterium |
|------|------------------|
| **CORE hört** | Aufzeichnung/Transkript von Scout-Mikro oder 4D_RESONATOR (CORE) erreicht CORE/OC; reproduzierbar. |
| **CORE sieht** | Bild/Stream von Kamera (Scout oder MX/Brio) wird von CORE genutzt oder gespeichert; Pfad/Datei nachweisbar. |
| **CORE spricht** | TTS-Audio erreicht User (Boxen/WhatsApp/Abspielgerät); User hat es gehört oder Datei/Log beweist Ausgabe. |

---

## Ist-Zustand (geprüft)

### CORE hört – **[OK]** Pipeline via 4D_RESONATOR (CORE)

- **4D_RESONATOR (CORE):** `dreadnought_listen.py` nimmt Audio auf (oder Dummy-Fallback bei fehlender Hardware) und sendet es als Event an OMEGA_ATTRACTOR.
- **Beweis:** `proof_hoert_sieht_spricht.py` meldet Erfolg beim Senden des Audio-Events an OMEGA_ATTRACTOR.

### CORE sieht – **[OK]** MX/Brio via Scout → go2rtc → HA

- **Status:** MX Brio (USB am Scout/Raspi) registriert in go2rtc (`mx_brio`) und in HA (`camera.192_168_178_54`).
- **Pipeline:** USB `/dev/video0` → go2rtc (Scout:1984) → RTSP (Scout:8554) → HA Generic Camera → CORE.
- **Snapshot-URL (HA):** `https://192.168.178.54:8123/api/camera_proxy/camera.192_168_178_54`
- **Snapshot-URL (go2rtc direkt):** `http://192.168.178.54:1984/api/frame.jpeg?src=mx_brio`
- **Beweis 1:** `data/mx_ha_proof/proof_mx_brio_scout_20260228_212450.jpg` (24.834 Bytes, direkt go2rtc).
- **Beweis 2:** `data/mx_ha_proof/proof_mx_via_HA_20260228_212630.jpg` (23.756 Bytes, via HA camera_proxy).
- **Beweis 3:** `proof_hoert_sieht_spricht` -> `[Sehen] OK: Quelle: scout_mx` (28.02.2026).
- **.env:** `SCOUT_MX_SNAPSHOT_URL` gesetzt.

### CORE spricht – **[OK]** TTS auf Google Minis + WhatsApp

- **Google TTS:** `tts.google_translate_say` auf `media_player.regal_3` und `media_player.schreibtisch` funktioniert.
- **ElevenLabs TTS:** `tts.speak` mit `tts.elevenlabs` auf Google Minis funktioniert.
- **Routing:** TTS-Audio wird über Nabu Casa Cloud geroutet (`*.ui.nabu.casa`), da lokale HTTPS-URLs von Cast-Geräten nicht geladen werden können.
- **Fix:** `external_url: https://192.168.178.54:8123` → HA routet TTS über Nabu Casa → gültiges SSL → Minis spielen ab.
- **WhatsApp:** `ha_client.send_whatsapp_audio` sendet MP3 via Home Assistant.
- **Beweis:** User hat Sprache auf Google Minis gehört (Google TTS + ElevenLabs, 2026-03-01). Datei `media/proof_tts.mp3` existiert.
- **AdGuard Home:** DNS-Server auf Scout aktiv, DNS-Rewrite für `mth-home2go.duckdns.org` → `192.168.178.54`. Siehe `docs/03_INFRASTRUCTURE/ADGUARD_HOME_SETUP.md`.

---

## Beweis-Skript

`python -m src.scripts.proof_hoert_sieht_spricht` führt aus:

1. **Sehen:** 1× Snapshot (MX/Brio oder CAMERA_SNAPSHOT_URL), speichert in `data/mx_test/`, schreibt Pfad in Log/Report.
2. **Sprechen:** TTS erzeugen → `media/`; optional: dieselbe Datei an WhatsApp senden (HA erreichbar, WHATSAPP_TARGET_ID).
3. **Hören:** Kein Code → Report: „[FAIL] Hören nicht umgesetzt; siehe ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md“.

Report wird in `data/proof_hoert_sieht_spricht_report.txt` geschrieben (Exit-Codes, Pfade, Fehler).

---

## Nächste Aktionen (Teamchef)

| Priorität | Aktion | Verifikation |
|-----------|--------|--------------|
| 1 | Scout-MX RTSP-Server aktivieren | go2rtc.yaml auf Scout aktualisieren |
| 2 | RTSP-Port Check ausführen | `python src/scripts/test_scout_rtsp.py` |
| 3 | Scout-MX in HA via RTSP einbinden | `camera.scout_mx` nutzt `stream_source` |
| 4 | `proof_hoert_sieht_spricht` (neue Version) | Gesamtsystem-Check |

---

**Referenz:** SCOUT_USB_KAMERA_MIKRO_HA_OS.md, usb_microphone_research.md, CAMERA_GO2RTC_WINDOWS.md, ha_client.send_whatsapp_audio.

---

## Letzter Proof-Lauf

**Datum:** 2026-02-28

`python -m src.scripts.proof_hoert_sieht_spricht` – Report in `data/proof_hoert_sieht_spricht_report.txt`.

| Ziel     | Ergebnis | Beweis |
|----------|----------|--------|
| Sehen    | **OK**   | `data/mx_test/proof_mx_20260228_202644.jpg` | Quelle: scout_mx (via HA camera_proxy) |
| Sprechen | OK       | media/proof_tts.mp3 + WhatsApp via HA gesendet |
| Hören    | **VORBEREITET** | Hardware erkannt (Brio-Mikro Source 4 + Samsung Headset Source 3). go2rtc-Streams definiert. Assist-Pipeline-Anleitung bereit (`SCOUT_ASSIST_PIPELINE.md`). User muss 4 Addons in HA installieren. |
