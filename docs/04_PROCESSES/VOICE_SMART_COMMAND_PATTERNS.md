<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Voice Assistant – Smart Command Patterns

Dokumentation der vom Smart Command Parser unterstützten Sprachbefehle.

**Modul:** `src/voice/smart_command_parser.py`  
**Integration:** `src/services/scout_direct_handler.py` (SCOUT_DIRECT_MODE)

---

## API

```python
from src.voice.smart_command_parser import parse_command, HAAction

# entities: Liste von HA-States (get_states) – für Entity Resolution
action = parse_command("Regal 80% Helligkeit", entities)
# -> HAAction(domain="light", service="turn_on", entity_id="light.led_regal", data={"brightness_pct": 80})
```

---

## Unterstützte Patterns

### 1. Ein/Aus/Toggle

| Befehl | Service | Beispiel |
|--------|---------|----------|
| `[entity] aus` | turn_off | "Regal aus", "Deckenlampe aus" |
| `[entity] an` / `[entity] ein` | turn_on | "Regal an", "Küche ein" |
| `Mach das [entity] aus/an` | turn_off/turn_on | "Mach das Regal aus" |
| `Licht [entity] aus` | turn_off | "Licht Regal aus" (Synonym ignoriert) |
| `[entity] umschalten` / `toggle` | toggle | "Regal umschalten" |

**Synonyme für Licht:** Licht, Lampe, Beleuchtung, Leuchte, Birne

---

### 2. Helligkeit

| Befehl | Service | data |
|--------|---------|------|
| `[entity] [0-100]% Helligkeit` | light.turn_on | brightness_pct |
| `[entity] [0-100]% hell` | light.turn_on | brightness_pct |

**Beispiele:** "Regal 80% Helligkeit", "Deckenlampe 50% hell"

---

### 3. Farbe

| Befehl | Service | data |
|--------|---------|------|
| `[entity] [farbe]` | light.turn_on | rgb_color |

**Unterstützte Farben:** rot, grün, blau, weiß, gelb, orange, lila, violett, türkis, rosa, warm, kalt

**Beispiele:** "Regal rot", "Deckenlampe blau"

---

### 4. Lautstärke (Media Player)

| Befehl | Service | Hinweis |
|--------|---------|---------|
| `Lautstärke [entity] um X% erhöhen` | media_player.volume_up | Relative Änderung |
| `Lautstärke [entity] um X% verringern` | media_player.volume_down | Relative Änderung |

**Beispiele:** "Lautstärke Fernseher um 20% erhöhen"

---

### 5. Temperatur (Climate)

| Befehl | Service | data |
|--------|---------|------|
| `Temperatur [entity] auf X Grad` | climate.set_temperature | temperature |

**Beispiele:** "Temperatur Wohnzimmer auf 21 Grad"

---

## Entity Resolution

- **Fuzzy-Match:** rapidfuzz gegen `friendly_name` und `entity_id`
- **Index:** entity_id-Kurzform (z.B. "regal") und friendly_name (z.B. "LED Regal")
- **Umlaute:** ä→ae, ö→oe, ü→ue, ß→ss

**Beispiele:**
- "Regal" → light.regal oder light.led_regal
- "Deckenlampe" → light.deckenlampe
- "Fernseher" → media_player.fernseher

---

## LLM-Fallback

Wenn kein hardcodiertes Pattern matcht:
- **Ollama** (lokal, bevorzugt)
- **Gemini** (Fallback)

Structured Output: `{domain, service, entity_id, data}`

---

## Integration

1. **Entities laden:** `data/home_assistant/states.json` (via `fetch_ha_data.py`) oder `context["entities"]`
2. **Scout Direct Handler:** Versucht Smart Parser zuerst, sonst Telemetry-Injector/LLM-Triage
3. **HA-Webhook:** `/webhook/ha_action`, `/webhook/inject_text` → `process_text()`

---

## Abhängigkeiten

- `rapidfuzz` (optional, für besseres Fuzzy-Matching)
- `langchain_ollama` / `langchain_google_genai` (LLM-Fallback)
