<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Custom Wake Word Training – „hey core“ und „computer“

**Zweck:** Anleitung zum Trainieren eigener openWakeWord-Modelle für CORE und Computer.

---

## 1. Google Colab – Wake Word Training

### 1.1 Link

**[Wake Word Training Environment](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing)**

### 1.2 Voraussetzungen

- Google-Konto
- Browser-Tab während des Trainings offen lassen (~30–60 Min.)
- Aktuell nur englische Wake Words unterstützt (Aussprache wird per Piper TTS generiert)

---

## 2. Schritte für „hey core“

1. **Colab öffnen:** Link oben → „Datei → Eine Kopie erstellen“ (eigene Kopie anlegen)
2. **target_word setzen:** In Sektion 1 `target_word = "hey core"` (oder `"core"` für kürzeres Wort)
3. **Aussprache prüfen:** Play-Button neben `target_word` klicken → Audio anhören
4. **Rechtschreibung anpassen:** Falls nötig, Schreibweise ändern (z.B. „hey core“ vs. „hey atläs“ für deutsche Aussprache)
5. **Runtime → Run all** ausführen
6. **Warten:** Ca. 30–60 Minuten (Colab-Ressourcen abhängig)
7. **Download:** `.tflite`-Datei aus dem Output herunterladen
8. **Dateiname:** z.B. `hey_atlas_v0.1.tflite` (Colab generiert den Namen)

### 2.1 Ablage auf Scout

- Samba: `\\192.168.178.54\share\openwakeword\`
- Oder: `scripts/setup_scout_wake_words.py` (siehe unten)
- Datei: `hey_atlas_v0.1.tflite` nach `/share/openwakeword/` kopieren

---

## 3. Schritte für „computer“

1. **Colab öffnen:** Gleicher Link wie oben
2. **target_word setzen:** `target_word = "computer"`
3. **Aussprache prüfen:** Play-Button → Audio anhören (englische Aussprache)
4. **Runtime → Run all** ausführen
5. **Warten:** Ca. 30–60 Minuten
6. **Download:** `.tflite`-Datei (z.B. `computer_v0.1.tflite`)
7. **Ablage:** Nach `/share/openwakeword/` auf Scout kopieren

---

## 4. Ablage auf Scout – Verzeichnis

| Pfad (Scout/HA)      | Beschreibung                          |
|----------------------|---------------------------------------|
| `/share/openwakeword`| Verzeichnis für Custom Wake Word Modelle |

**Namenskonvention:** `{wakeword}_v{version}.tflite` (z.B. `hey_atlas_v0.1.tflite`, `computer_v0.1.tflite`)

Das openWakeWord Add-on scannt dieses Verzeichnis automatisch. Nach dem Kopieren:

- Home Assistant neu starten **oder**
- openWakeWord Add-on neu starten

---

## 5. Bekannte Einschränkungen

- **Sprache:** Colab nutzt Piper TTS – aktuell nur englische Aussprache
- **tflite-Konvertierung:** Gelegentlich Fehler bei ONNX→tflite; bei Problemen [Issue #251](https://github.com/dscripka/openWakeWord/issues/251) prüfen
- **Ressourcen:** Colab Free Tier kann bei hoher Auslastung langsam sein

---

## 6. Referenzen

| Thema              | URL |
|--------------------|-----|
| Colab Training     | https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb |
| HA Wake Words      | https://www.home-assistant.io/voice_control/create_wake_word/ |
| openWakeWord       | https://github.com/dscripka/openWakeWord |
| Scout Setup        | [SCOUT_WAKE_WORD_SETUP.md](SCOUT_WAKE_WORD_SETUP.md) |
