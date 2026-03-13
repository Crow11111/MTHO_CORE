<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE TTS Browser-Integration (Tampermonkey)

**Zweck:** Markierten Text im Browser direkt an CORE senden und lokal als Sprache abspielen.

---

## Übersicht

Mit `Strg + Shift + S` wird markierter Text an den lokalen CORE-Backend-Server gesendet, der ihn via ElevenLabs in Sprache umwandelt und auf dem PC abspielt.

```
Browser (Gemini, ChatGPT, etc.)
    ↓ Strg+Shift+S
Tampermonkey GM_xmlhttpRequest (umgeht CORS)
    ↓ POST JSON
http://localhost:8000/api/core/speak
    ↓
ElevenLabs TTS → MP3 → Lokale Wiedergabe (PC-Lautsprecher)
```

---

## 1. Voraussetzung: CORE Backend muss laufen

```batch
START_ATLAS_DIENSTE.bat
```

Oder manuell:
```powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Backend läuft dann auf: `http://localhost:8000`

---

## 2. Tampermonkey-Skript installieren

1. Tampermonkey Browser-Extension installieren (Chrome/Firefox/Edge)
2. Neues Skript erstellen
3. Folgenden Code einfügen:

```javascript
// ==UserScript==
// @name         CORE TTS Push
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Pusht markierten Text direkt an den lokalen CORE TTS-Server
// @match        https://gemini.google.com/*
// @match        https://chat.openai.com/*
// @match        https://chatgpt.com/*
// @match        https://claude.ai/*
// @match        https://*/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    // === CORE KONFIGURATION ===
    const LOCAL_PORT = 8000;
    const ENDPOINT_URL = `http://127.0.0.1:${LOCAL_PORT}/api/core/speak`;
    
    // Verfügbare Rollen: atlas_dialog, atlas_info, therapeut, analyst, atlas_high_density
    const DEFAULT_ROLE = "atlas_dialog";

    function pushToATLAS(text) {
        GM_xmlhttpRequest({
            method: "POST",
            url: ENDPOINT_URL,
            data: JSON.stringify({ 
                text: text,
                role: DEFAULT_ROLE
            }),
            headers: {
                "Content-Type": "application/json"
            },
            onload: function(response) {
                console.log("CORE-TTS: Wird abgespielt.", response.responseText);
                // Grüner Rahmen = Erfolg
                document.body.style.boxShadow = "inset 0 0 15px #0f0";
                setTimeout(() => document.body.style.boxShadow = "none", 800);
            },
            onerror: function(error) {
                console.error("CORE-TTS Error: Backend nicht erreichbar.", error);
                // Roter Rahmen = Fehler
                document.body.style.boxShadow = "inset 0 0 15px #f00";
                setTimeout(() => document.body.style.boxShadow = "none", 800);
            }
        });
    }

    // Shortcut: STRG + SHIFT + S
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.code === 'KeyS') {
            e.preventDefault(); // Verhindert Browser-Save-Dialog
            
            let selectedText = window.getSelection().toString().trim();
            
            if (selectedText.length > 0) {
                console.log("CORE-TTS: Sende", selectedText.length, "Zeichen...");
                pushToATLAS(selectedText);
            } else {
                console.warn("CORE-TTS: Kein Text markiert.");
                // Gelber Rahmen = Warnung
                document.body.style.boxShadow = "inset 0 0 15px #ff0";
                setTimeout(() => document.body.style.boxShadow = "none", 500);
            }
        }
    });
    
    console.log("CORE TTS Push geladen. Shortcut: Strg+Shift+S");
})();
```

4. Speichern (Strg+S)

---

## 3. Nutzung

1. **Backend starten:** `START_ATLAS_DIENSTE.bat`
2. **Browser öffnen:** Gemini, ChatGPT, Claude, oder beliebige Seite
3. **Text markieren** (mit Maus oder Shift+Pfeiltasten)
4. **Strg + Shift + S** drücken
5. **Audio wird auf PC-Lautsprechern abgespielt**

### Visuelles Feedback:
- **Grüner Rahmen:** Erfolgreich gesendet, wird abgespielt
- **Roter Rahmen:** Backend nicht erreichbar
- **Gelber Rahmen:** Kein Text markiert

---

## 4. API-Referenz

### POST `/api/core/speak`
Kurzform - spielt sofort ab.

**Request:**
```json
{
    "text": "Der zu sprechende Text",
    "role": "atlas_dialog"
}
```

**Response:**
```json
{
    "status": "ok",
    "played": true,
    "path": "c:\\CORE\\media\\tts_abc123.mp3"
}
```

### POST `/api/core/tts`
Vollversion mit allen Optionen.

**Request:**
```json
{
    "text": "Der zu sprechende Text",
    "role": "atlas_dialog",
    "state_prefix": "",
    "play": true
}
```

**Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `text` | string | (required) | Der zu sprechende Text |
| `role` | string | `atlas_dialog` | Stimme/Rolle aus voice_config |
| `state_prefix` | string | `""` | Emotionaler State-Prefix |
| `play` | bool | `true` | `true` = lokal abspielen, `false` = MP3 zurückgeben |

### GET `/api/core/voice/roles`
Listet alle verfügbaren Rollen/Stimmen.

**Response:**
```json
{
    "roles": ["atlas_high_density", "atlas_info", "atlas_dialog", "therapeut", "analyst"],
    "roles_with_voice_id": [...]
}
```

---

## 5. Verfügbare Stimmen/Rollen

| Rolle | Beschreibung |
|-------|--------------|
| `atlas_dialog` | Standard-Konversationsstimme |
| `atlas_info` | Neutrale Info-Stimme |
| `atlas_high_density` | Komprimierte, schnelle Ausgabe |
| `therapeut` | Ruhige, empathische Stimme |
| `analyst` | Analytische, sachliche Stimme |

---

## 6. Troubleshooting

### "Backend nicht erreichbar" (roter Rahmen)
- Prüfen ob Backend läuft: `http://localhost:8000/docs`
- `START_ATLAS_DIENSTE.bat` ausführen

### Kein Audio
- ElevenLabs API-Key prüfen (`.env`: `ELEVENLABS_API_KEY`)
- Lautsprecher/Audio-Ausgabe prüfen

### CORS-Fehler
- Tampermonkey nutzt `GM_xmlhttpRequest`, das CORS umgeht
- Falls trotzdem Fehler: `@connect localhost` und `@connect 127.0.0.1` im Skript-Header prüfen

---

## 7. Erweiterung: Stimme per Shortcut wechseln

Für Power-User: Verschiedene Shortcuts für verschiedene Stimmen:

```javascript
// Strg+Shift+S = atlas_dialog
// Strg+Shift+T = therapeut  
// Strg+Shift+A = analyst

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey) {
        let role = null;
        if (e.code === 'KeyS') role = 'atlas_dialog';
        if (e.code === 'KeyT') role = 'therapeut';
        if (e.code === 'KeyA') role = 'analyst';
        
        if (role) {
            e.preventDefault();
            let text = window.getSelection().toString().trim();
            if (text) pushToATLAS(text, role);
        }
    }
});
```
