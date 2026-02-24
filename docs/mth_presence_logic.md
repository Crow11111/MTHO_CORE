# Robuste Anwesenheitserkennung ohne KI-Overhead (ATLAS Standard)

Die sicherste und schnellste Methode, um deine Anwesenheit zu tracken, ist ein kombiniertes System direkt in Home Assistant (YAML). 

Anstatt Ollama alle paar Minuten zu fragen (was extrem viel Rechenleistung kostet und fehleranfällig ist) oder simple "if/else" Boolean-Sprawls zu pflegen, die nach 3 Jahren unübersichtlich werden, nutzen wir den **ATLAS Standard: Bayesian Sensors & Proximity**.

---

## Schritt 1: Der Bayesian Sensor (Die Core-Logik)
Anstelle von harten JA/NEIN-Regeln nutzen wir Wahrscheinlichkeiten.
Füge diesen Code in deine `configuration.yaml` ein. Das vereint dein iPhone, die Custom App (mthone), Türen und deinen PC zu einem einzigen intelligenten virtuellen Presence-Wert.

```yaml
binary_sensor:
  - platform: bayesian
    name: "MTH Real Presence (Bayesian)"
    unique_id: mth_real_presence_bayesian
    prior: 0.3    # Grundwahrscheinlichkeit, dass du generell Zuhause bist
    probability_threshold: 0.85 # Sensor schlägt bei über 85% Zuversicht an
    observations:
      # 1. GPS/FindMy Tracking (Sehr hohes Gewicht)
      - entity_id: 'device_tracker.iphone_2'
        prob_given_true: 0.95
        prob_given_false: 0.1
        platform: 'state'
        to_state: 'home'
        
      # 2. PC Activity (Sehr hohes Gewicht, falls du am Rechner sitzt)
      - entity_id: 'sensor.pc_status'
        prob_given_true: 0.90
        prob_given_false: 0.4 # Auch wenn der PC aus ist, könntest du schlafen/zuhause sein
        platform: 'state'
        to_state: 'Active'
        
      # 3. Bewegungsmelder Flur / Haustür (Zusätzlicher Indikator)
      # WICHTIG: Ignoriert den Sensor, wenn "Zylon Prime" (Staubsauger) gerade reinigt!
      - platform: 'template'
        value_template: >
          {{ is_state('binary_sensor.front_door', 'on') 
             and not is_state('vacuum.zylon_prime', 'cleaning') 
             and not is_state('vacuum.zylon_prime', 'returning') }}
        prob_given_true: 0.70
        prob_given_false: 0.3
```



## Schritt 3: Die Unified Automation (Die Exekutive)
Jetzt ersetzen wir deine vielen kleinen Automations ("mth_in_h91", "mth_realy_not_in_h91", etc.) durch EINE einzige, clevere Automation. 

Diese Automation triggert deine alten, vertrauten Input Booleans (`input_boolean.mth91`, `input_boolean.mth_away`), sodass **alle deine bestehenden Scripte der letzten 3 Jahre weiterhin ohne Änderung funktionieren!**

Du kannst beim Erstellen einer neuen Automation oben rechts auf die 3 Punkte -> "Als YAML bearbeiten" klicken und das hier einfügen:

```yaml
alias: "System: ATLAS Presence Director"
description: "Ersetzt das alte Boolean-Sprawl durch eine saubere Bayes'sche und Proximity-Steuerung."
mode: queued
trigger:
  # Trigger 1: Bayesian bestätigt Anwesenheit > 85%
  - platform: state
    entity_id: binary_sensor.mth_real_presence_bayesian
    to: "on"
    id: "confirmed_home"

    
  # Trigger 3: Du bist endgültig weg
  - platform: state
    entity_id: binary_sensor.mth_real_presence_bayesian
    to: "off"
    for: "00:05:00" # 5 Minuten Ausfallpuffer (z.B. kurzer WLAN Drop)
    id: "confirmed_away"

action:

      # WENN MTH DEFINITIV ZUHAUSE IST
      - conditions:
          - condition: trigger
            id: "confirmed_home"
        sequence:
          - service: input_boolean.turn_on
            target:
              entity_id: input_boolean.mth91
          - service: input_boolean.turn_off
            target:
              entity_id: input_boolean.mth_away

      # WENN MTH DEFINITIV WEG IST
      - conditions:
          - condition: trigger
            id: "confirmed_away"
        sequence:
          - service: input_boolean.turn_off
            target:
              entity_id: input_boolean.mth91
          - service: input_boolean.turn_on
            target:
              entity_id: input_boolean.mth_away
          # (Optional) Shutdown Script aufrufen
          # - service: script.house_shutdown
```

---

## Warum ist diese Architektur einem einfachen Template (oder KI) überlegen?
1. **Ausfallsicher durch Fuzzy Logic:** Wenn der Handyakku stirbt, du aber vor 10 Minuten am PC getippt hast oder am Bewegungsmelder im Flur vorbeigegangen bist, berechnet Home Assistant mathematisch, dass du immer noch da bist. Das verhindert das gefürchtete "Licht Aus", nur weil ein Sensor (z.B. iPhone Ping) hakt.
2. **Elegante Roboter-Toleranz (Zylon Prime):** Dank des `value_template` im Bayesian Sensor schließen wir *Zylon Prime* komplett aus der Rechnung aus, während er saugt. Keine komplizierten 20-Minuten-Cool-Down Zähler mehr im Welcome Script! Wenn der Flur triggert und der Sauger läuft, ignoriert die Präsenz-Zentrale das einfach.
3. **Abwärtskompatibel:** Die alte Logik über `input_boolean.mth91` ist über Jahre gewachsen. Diese bleiben der "Point of Truth" für deine anderen Scripte, aber der "Entscheidungs-Motor" dahinter ist jetzt Enterprise-Qualität.
