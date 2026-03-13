# Übergabe 28.02.2026 ~04:00

## Erledigt

1. **OpenClaw VPS (187.77.68.250)** - Re-Deployed. Config-Persistence repariert: `deploy_vps_full_stack.py` mergt jetzt existierende `openclaw.json` statt sie zu überschreiben. Container laufen (Port 18789 Admin, 18790 Spine).
2. **OpenClaw sauber neu aufgesetzt (28.02. Nachmittag)** – Hostinger-Container `openclaw-ntw5` gestoppt. Nur noch **openclaw-admin** (eigene Instanz) aktiv. **Gemini 3.1 Pro** mit eigenem API-Key in `openclaw.json` (baseUrl gesetzt). **Nginx Reverse Proxy** mit HTTPS vor OpenClaw; **WhatsApp-Session** zurückgesetzt für frisches Pairing.
   - **Zugriff UI:** **https://187.77.68.250/** (Browser: Zertifikatswarnung bestätigen → „Erweitert“ → „Fortsetzen“). Token: `.env` → `OPENCLAW_GATEWAY_TOKEN`.
   - Nginx-Config: `nginx_openclaw_https.conf` (im Repo); auf VPS: `/etc/nginx/sites-available/openclaw-https.conf`.
3. **Präsenz-Automation** - `automation.system_atlas_presence_director` (ID: `atlas_presence_director`) repariert. Alter Trigger war `binary_sensor.mth_real_presence_bayesian` (existierte nie, halluziniert). Neuer Trigger: `device_tracker.iphone_2` direkt. Home → `input_boolean.mth91` AN / `input_boolean.mth_away` AUS. Away (5 Min Puffer) → umgekehrt.
4. **Hardware-Recherche** - Google Coral USB Accelerator: ~80-85€ bei BerryBase (B-Ware) oder WElectron (84,90€).
5. **Scout Dockerfile** - Wurde für TPU/Audio vorbereitet, aber: Scout ist HA OS, KEIN Docker-Deployment-Ziel von außen. Dieser Ansatz war falsch. Dateien `docker/scout/Dockerfile` und `src/edge/audio_player.py` sind Code-Vorlagen, aber nicht direkt auf dem Scout deploybar.

## Offen (Priorität)

### A. OpenClaw UI prüfen
- User sagt: "wenn ich da drauf will, komm ich rein, aber drinnen ist nicht angemeldet, keine Fähigkeiten, Skills, Verknüpfungen etc."
- Nach dem Re-Deploy mit Merge-Logik prüfen ob das UI jetzt korrekt konfiguriert ist.
- URL: `http://187.77.68.250:18789`
- Token: siehe `.env` → `OPENCLAW_GATEWAY_TOKEN`

### B. Präsenz-Erkennung vervollständigen
- **mmWave Sensor** (`_TZE200_bdb16fsr`): User sucht ihn noch (liegt im Schrank, nicht angeschlossen). DDF-Datei liegt bereit: `c:\CORE\tuya_mmwave_sensor.json`. Muss auf Raspi in deCONZ eingespielt werden (Phoscon "Edit DDF" oder Dateisystem).
- **Alte Automations aufräumen**: `automation.mthone_in_h91`, `automation.mthone_leave_h91`, `automation.auto_check_mth_in_h91` etc. könnten mit der neuen `atlas_presence_director` kollidieren.  Sicherung machen, dann deaktivieren.
- **Master-Switches**: `input_boolean.mth91` und `input_boolean.mth_away` sind die zentralen Schalter. Alles andere (Welcome Scripts, Licht, Heizung) hängt daran.

### C. Scout: Was wird dort gebraucht?
- Scout = Raspberry Pi 5, 8GB, Home Assistant OS.
- Kein Docker von außen. Erweiterungen laufen als HA-Addons oder direkt in HA (Automations, Integrations).
- Audio-Output: Über HA → Google Nest Mini (Cast). Nicht über einen eigenen Docker-Container.
- TPU: Wenn Coral USB Accelerator gekauft, als USB-Device am Raspi. Nutzung über Frigate-Addon oder deCONZ.

### D. Allgemeine Direktive
- **Böser Chef Modus**: Nichts glauben, alles beweisen lassen. Vor jedem Schreibzugriff auf HA-Dashboards: Backup. Vor jedem Deploy: Dry-Run.
- **Sprache**: Deutsch.
- **Token-Druck**: Subagents bekommen minimalen Kontext, keine Romane.

## Relevante Dateien
- `src/scripts/deploy_vps_full_stack.py` - VPS Full-Stack Deployment (mit Merge-Fix)
- `src/scripts/fix_presence_automation.py` - Präsenz-Reparatur
- `docs/mth_presence_logic.md` - Geplante Bayesian-Architektur (noch nicht umgesetzt)
- `tuya_mmwave_sensor.json` - DDF für mmWave Sensor
- `docs/02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md` - OpenClaw Rollen
- `.env` - Alle Keys und Zugänge
