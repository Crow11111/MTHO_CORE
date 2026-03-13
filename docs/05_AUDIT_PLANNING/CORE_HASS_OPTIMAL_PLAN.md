<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE HASS Optimal Plan

## 1. Entity-Matrix (Leichen-Abgleich)

| Entität | Integration | Original Name | Status (Registry) | Im Dashboard genutzt? |
|---------|-------------|---------------|-------------------|-----------------------|
| `automation.h91_verlassen` | automation | ALT AUTO H91 verlassen ALT | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new |
| `automation.tapo_alarm_ansicht` | automation | Tapo Alarm Ansicht | Active (in Registry) | None |
| `button.tapo_c52a_schwenk_nach_rechts` | tplink | Schwenk nach rechts | Active (in Registry) | lovelace.dashboard_cam |
| `button.tapo_reboot` | tapo_control | Tapo Reboot | Active (in Registry) | None |
| `device_tracker.esp_15da12` | fritz | ESP-15DA12 | Active (in Registry) | None |
| `device_tracker.esp_birne11` | fritz | ESP-Birne11 | Active (in Registry) | None |
| `device_tracker.esp_birne2_old` | fritz | esp-birne2-old | Active (in Registry) | None |
| `device_tracker.esp_fenster` | fritz | ESP-Fenster | Active (in Registry) | None |
| `device_tracker.espleddecke` | fritz | espleddecke | Active (in Registry) | None |
| `device_tracker.ipad_neu` | mobile_app | iPad neu | Active (in Registry) | None |
| `device_tracker.ipad_von_mth` | mobile_app | iPad von MtH | Active (in Registry) | None |
| `device_tracker.ipad_von_ulla` | fritz | iPad | Active (in Registry) | None |
| `device_tracker.ipadneueswlan` | fritz | ipadneueswlan | Active (in Registry) | None |
| `device_tracker.iphone` | fritz | iPhone-von-MtH | Active (in Registry) | None |
| `device_tracker.s20_von_marc` | fritz | S20-von-Marc | Active (in Registry) | lovelace.dashboard_new |
| `light.alle` | group | Alle | Active (in Registry) | lovelace.dashboard_new, lovelace.test_mush |
| `light.dayoff` | group | DayOff | Active (in Registry) | lovelace.dashboard_new |
| `light.govee_light` | govee_ble_lights | GOVEE Light | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new |
| `light.hauptbeleuchtung` | group | Hauptbeleuchtung | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new, lovelace.test_mush |
| `light.led_pc` | tuya | None | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new, lovelace.test_mush |
| `light.led_sofa` | flux_led | None | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new, lovelace.test_mush |
| `scene.govee_to_mqtt_one_click_farbig_nachtgluhen` | mqtt | One-Click: Farbig: Nachtglühen | Active (in Registry) | None |
| `select.tapo_move_to_preset` | tapo_control | Tapo Move to Preset | Active (in Registry) | None |
| `switch.kueche_kuel` | localtuya | Monitor2 | Active (in Registry) | None |
| `switch.kueche_main` | tuya | Steckdose 1 | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new |
| `switch.stecker` | group | Stecker | Active (in Registry) | lovelace.dashboard_sa, lovelace.dashboard_new |

## 2. Add-on Audit (Läuft vs. Weg)
> **Status-Hinweis:** Der automatische API-Abruf via `HASS_TOKEN` schlug fehl (401 Unauthorized, Token abgelaufen). Der SSH-Zugang (`dreadnought`) hat keine Berechtigung für die Supervisor-CLI (`ha addons`).
> 
> **Empfohlener manueller Check (Einstellungen -> Add-ons):**
- **Unnötig/Gestoppt:** Alte Add-ons (z.B. alte SSH/Samba Instanzen, verwaiste DB-Browser), die nicht mehr gestartet werden, komplett deinstallieren.
- **Fehlerhaft:** Add-ons mit Watchdog-Restarts prüfen (Logs).




## 3. ADD-ON AUDIT (HOST LEVEL - DOCKER)

> **Quelle:** SSH Host 192.168.178.54 (dreadnought) | **Methode:** `docker ps`

### ⛔ BLOCKED: PROTECTION MODE ACTIVE

**Das SSH Add-on läuft im 'Protection Mode'. Zugriff auf Docker und HA CLI ist blockiert.**

#### Lösungsschritte:

1. Gehe im Home Assistant zu **Einstellungen -> Add-ons -> Advanced SSH & Web Terminal**.

2. Deaktiviere den Schalter **Protection mode**.

3. Starte das Add-on neu.

4. Führe dieses Audit erneut aus.


## 4. Masterplan für sauberen HA-Core

### Schritt 1: Dashboard- und YAML-Sanierung (Priorität 1)
- Alle betroffenen Dashboards (siehe Matrix) von den toten Entitäten befreien.
- **YAML/Automatisierungen:** Vor dem Löschen der Entitäten aus der Registry müssen diese aus allen `automations.yaml` und `scripts.yaml` entfernt werden (siehe `HA_ENTITY_CLEANUP_PLAN.md` -> Gefahrenzonen), um Boot-Fehler (Template Errors) zu vermeiden.

### Schritt 2: Hard-Delete in der Entity Registry (Priorität 2)
- **Kategorie A (Absolute Leichen):** Über die UI (`Einstellungen -> Entitäten` -> nach `Nicht verfügbar` filtern) hart löschen.
- Falls die UI es verweigert (z.B. Integration blockiert): Die entsprechenden Integrationen für `iphone`, `ipad`, `esp_` etc. (meist `mobile_app` oder `esphome`) direkt in `Geräte & Dienste` löschen.

### Schritt 3: Wackelkandidaten (Priorität 3)
- Für verbliebene Entitäten der Kategorie B (z.B. `light.led_sofa`) die entsprechende Integration (`tuya`, `govee`, `mqtt`) neu laden (`Reload`).
- Falls sie nicht zurückkehren: Ebenfalls nach YAML-Prüfung aus der Registry entfernen.
