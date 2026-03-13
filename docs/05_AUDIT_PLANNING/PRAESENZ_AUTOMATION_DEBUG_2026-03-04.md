<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# HA Präsenz-Automatisierung Debug – 2026-03-04

## Identifiziertes Problem

**Ursache:** Die CORE Presence Director Automation triggerte auf `device_tracker.iphone_2` mit States `home`/`not_home`. Der iCloud3/iPhone Device Tracker liefert jedoch **"H91"** (Zone-Name von `zone.home_2`) statt `"home"` wenn Marc zuhause ist.

- `device_tracker.iphone_2`: State = **H91** (in Zone) oder **not_home** (außerhalb)
- `person.marc_ten_hoevel`: State = **H91** oder **home** (je nach Zone) bzw. **not_home**

Die Trigger `to: "home"` und `from: "home"` wurden nie erreicht → mth91/mth_away wurden nicht aktualisiert → Welcome/Standby-Scripts blieben stumm.

## Durchgeführter Fix

1. **Trigger-Entity:** `device_tracker.iphone_2` → `person.marc_ten_hoevel` (aggregiert alle Trackers)
2. **States:** Beide Zonen abgedeckt:
   - Ankommen: `to: "home"` ODER `to: "H91"`
   - Abfahrt: `from: "home"`/`from: "H91"` → `to: "not_home"` (5 Min Puffer)

## Betroffene Kette

```
person.marc_ten_hoevel (home/H91/not_home)
    → CORE Presence Director
        → input_boolean.mth91 / input_boolean.mth_away
            → NEW Welcome Hook, Home > Wlcome on, Zylon Dock > welcome on
                → script.welcome, script.welcome_a, scene.standby
```

## Test-Anleitung

1. **Manueller Test (Ankommen):**
   - In HA: `person.marc_ten_hoevel` State prüfen (sollte H91 oder home sein wenn zuhause)
   - `input_boolean.mth91` sollte `on`, `input_boolean.mth_away` sollte `off` sein

2. **Abfahrt simulieren:**
   - HA Developer Tools → States: `person.marc_ten_hoevel` temporär auf `not_home` setzen (nur zum Test)
   - Oder: 5+ Min warten bis GPS tatsächlich not_home meldet
   - Erwartung: Nach 5 Min → mth91=off, mth_away=on, ggf. scene.standby

3. **Rückkehr:**
   - Wenn Person von not_home → H91 oder home wechselt
   - Erwartung: mth91=on, mth_away=off, Welcome-Automationen triggern

4. **Debug-Skript erneut ausführen:**
   ```bash
   python -m src.scripts.debug_presence_automation
   ```

## Dateien

- `src/scripts/debug_presence_automation.py` – Live-Analyse
- `src/scripts/fix_presence_automation.py` – Automation-Update (bereits angewendet)
- `data/home_assistant/debug_presence.json` – Export der letzten Analyse
