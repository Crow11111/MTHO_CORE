<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# HA Phantom-Entitäten Cleanup Plan

## Zusammenfassung
- **Gesamtanzahl toter Entitäten:** 425 (Status `unavailable` / `unknown`)
- **Top-Domains:** switch (90), sensor (77), button (71), light (54), scene (34), device_tracker (33)

---

## 🛑 Kategorie A: Absolute Leichen (Sicher zu löschen)
Diese Entitäten gehören zu alten Geräten (IPads, ESPs, ausrangierte Kameras) und können ohne Bedenken aus der Registry entfernt werden.
*Beispiele (92 insgesamt):*
- **ESP/Eigenbauten:** `device_tracker.esp_15da12`, `device_tracker.esp_birne11`, `device_tracker.esp_birne2_old`, `device_tracker.esp_fenster`, `device_tracker.espleddecke`
- **Smartphones/Tablets:** `device_tracker.ipad_neu`, `device_tracker.ipad_von_mth`, `device_tracker.ipad_von_ulla`, `device_tracker.iphone`, `device_tracker.ipadneueswlan`, `device_tracker.s20_von_marc`
- **Tapo Kameras/Alte Hardware:** `button.tapo_c52a_schwenk_nach_rechts`, `automation.tapo_alarm_ansicht`, `button.tapo_reboot`

---

## ⚠️ Kategorie B: Wackelkandidaten (Prüfung erforderlich)
Diese Entitäten (333 Stück) sind potenziell temporär offline (z. B. physischer Lichtschalter betätigt, Gerät ohne Strom) oder tief in Logik verwurzelt.
*Beispiele:*
- **Beleuchtung (54):** `light.alle`, `light.dayoff`, `light.govee_light`, `light.led_sofa`, `light.hauptbeleuchtung`
- **Szenen (34):** Viele Szenen sind *unavailable*, oft weil zugrundeliegende Geräte der Szene fehlen.
- **Steckdosen/Schalter (90):** `switch.kueche_main`, `switch.stecker`

**Test-Strategie für Kategorie B:**
1. **Physischer Check:** Stromzufuhr der betroffenen Leuchtmittel/Steckdosen prüfen.
2. **Ping/Verfügbarkeit:** Wenn das Gerät im Netzwerk (z.B. über die Zigbee2MQTT Map oder Unifi) nicht mehr gelistet ist > Zu Kategorie A verschieben.
3. **Integration Reload:** Betroffene Integration (z.B. Govee, Tuya) neu laden, um zu sehen, ob die Entität wieder aufwacht.

---

## 🚨 Gefahrenzonen (Code-Abhängigkeiten)
Von den 425 Leichen werden **43 in aktiven YAML-Dateien referenziert**! Das Löschen oder Fehlen dieser Entitäten führt zu defekten Automatisierungen (Hänger, Error Logs, unvollständige Ausführung).

### Kritische Automatisierungen (Auszug)
- **`device_tracker.iphone`** blockiert `COREne leave H91` und `666 Check MTH else off`
- **`device_tracker.s20_von_marc`** blockiert `AAAA AUTO TEST AAAAAA`
- **`automation.h91_verlassen`** (Leiche) ist Teil von `FORCE H91 OFF` / `FORCE H91` und dem Script `ausuraus manuell`
- **`light.led_sofa`** fehlt in `Florentine`, `Moin`, `Nachtpinkeln`, `Guten Morgen`
- **`light.led_pc`** fehlt in `Low Light Mode`, `Auto Pisslicht`, `Matrazte`
- **`switch.kueche_kuel` / `kueche_main`** fehlen in `Auto Kühl Check An`
- **`select.tapo_move_to_preset`** blockiert das Script `Wäschetimer`
- **`scene.govee_to_mqtt_one_click_farbig_nachtgluhen`** blockiert `Hörspielende variabel`

---

## ⚙️ Prozess-Empfehlung für Deployment-Team

1. **Backup:** Vor dem Löschen IMMER ein Full-Backup (Core + Addons) in HA ziehen.
2. **YAML-Sanierung (ZUERST!):**
   - Entferne die oben genannten *Gefahrenzonen*-Entitäten aus den Automatisierungen/Scripten ODER ersetze sie durch aktive Entitäten.
   - Grund: Löscht man eine Entität, die noch referenziert wird, wirft HA beim nächsten Neustart oder bei der Ausführung massive Fehler.
3. **Purge Phase 1 (Kategorie A):**
   - In HA: `Einstellungen` -> `Geräte & Dienste` -> `Entitäten`
   - Filter nach Zustand: `Nicht verfügbar`
   - Suche nach `esp`, `tapo`, `ipad`, `iphone`, etc.
   - Haken setzen -> `Ausgewählte löschen`
4. **Purge Phase 2 (Kategorie B):**
   - Für jede Lampe/Steckdose prüfen: Ist das Gerät wirklich weg?
   - Falls ja -> Aus Automatisierungen entfernen -> Löschen.
5. **Reload & Check:**
   - Gehe zu `Entwicklerwerkzeuge` -> `YAML überprüfen` -> Wenn grün, dann Automatisierungen neu laden.
   - `Einstellungen` -> `System` -> `Logs` checken auf "Template-Fehler" oder fehlende Entitäten.