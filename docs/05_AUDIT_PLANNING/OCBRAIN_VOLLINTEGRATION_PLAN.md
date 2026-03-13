<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OCBrain Vollintegrations-Plan

**Datum:** 2026-03-01  
**Status:** AKTIONSBEREIT  
**Axiom:** "Geht nicht" ist keine akzeptierte Antwort.

---

## 0. IST-Zustand (Faktencheck)

### Infrastruktur
| Komponente | Status | Beweis |
|---|---|---|
| VPS 187.77.68.250 | **ONLINE** | SSH Port 22 erreichbar, Port 18789 erreichbar |
| OpenClaw Gateway | **KONFIGURIERT** | `.env` Zeile 60: `OPENCLAW_GATEWAY_TOKEN="ykKqxCcMM5CPYTS20fxTWyu6RkLkvd5T"` |
| VPS_HOST | **GESETZT** | `.env` Zeile 56: `VPS_HOST="187.77.68.250"` |
| OPENCLAW_ADMIN_VPS_HOST | **GESETZT** | `.env` Zeile 64: `OPENCLAW_ADMIN_VPS_HOST="187.77.68.250"` |
| GEMINI_API_KEY | **GESETZT** | `.env` Zeile 15 |
| ELEVENLABS_API_KEY | **GESETZT** | `.env` Zeile 91 |
| ElevenLabs Voice IDs | **GESETZT** | `.env` Zeilen 92-93 + `voice_config.py` (14 Rollen) |
| ANTHROPIC_API_KEY | **GESETZT** | `.env` Zeile 86 |
| NEXOS_API_KEY | **GESETZT** | `.env` Zeile 95 |

### Erkenntnis
Die .env-Variablen für OpenClaw sind **NICHT auskommentiert** – sie sind vollständig befüllt. Das Template (`.env.template`) hat sie auskommentiert als Beispiel, aber die aktive `.env` hat alle Werte gesetzt. **Das Problem liegt also nicht an fehlenden .env-Variablen**, sondern an Integrationslücken in der Pipeline-Verkettung.

---

## 1. Lückenanalyse

### Lücke 1: OCBrain-Konnektivität verifizieren

| Feld | Wert |
|---|---|
| **Lücke** | OCBrain ist konfiguriert, aber Erreichbarkeit wurde nicht verifiziert (Docker-Container auf VPS läuft?) |
| **Warum jetzt nicht** | Kein automatischer Health-Check beim Start; `docker-compose.yml` definiert `atlas_net` als `external: true` – Netzwerk muss manuell erstellt werden |
| **Harte Grenze?** | **Nein** (Noch-nicht). Alle Credentials vorhanden, VPS erreichbar |
| **Konkrete Lösung** | 1. SSH auf VPS: `docker ps` prüfen ob `atlas_agi_core`, `atlas_postgres_state`, `atlas_chroma_state` laufen. 2. Falls nicht: `docker network create atlas_net && cd /opt/core-core/docker/agi-state && docker compose up -d`. 3. Health-Endpoint testen: `curl http://localhost:18789/` vom VPS. 4. Von 4D_RESONATOR (CORE): `python -c "from src.network.openclaw_client import check_gateway; print(check_gateway())"` |
| **Komplexität** | **NIEDRIG** (5 Min, 3 Befehle) |

### Lücke 2: WhatsApp-Audio → Transkript lokal → Text an OC

| Feld | Wert |
|---|---|
| **Lücke** | `whatsapp_audio_processor.py` transkribiert Audio via Gemini und gibt Analyse zurück – aber das Ergebnis wird **NIE an OCBrain weitergeleitet**. In `whatsapp_webhook.py` Zeile 92 geht die Antwort direkt per `ha_client.send_whatsapp()` zurück an den Sender. OC sieht die Sprachnachricht nie. |
| **Warum jetzt nicht** | Pipeline wurde als Gemini-Only gebaut: Audio → Gemini Transkript → Gemini Analyse → WhatsApp zurück. OC-Integration wurde übersprungen. |
| **Harte Grenze?** | **Nein** (Noch-nicht). Alle Bausteine existieren: `send_message_with_context()` ist fertig, Gemini-Transkription funktioniert. |
| **Konkrete Lösung** | In `whatsapp_webhook.py`, Funktion `run_audio()` (Zeile 89-92) erweitern: |
| | 1. Gemini-Transkript erstellen (existiert: `process_whatsapp_audio()`) |
| | 2. Transkript-Text an OCBrain senden: `send_message_with_context(f"WhatsApp-Sprachnachricht von {sender}: {transcript}", agent_id="main")` |
| | 3. OC-Antwort als erweiterte Antwort zurück an WhatsApp senden |
| | 4. Alternativ: Transkript + OC-Antwort beide an WhatsApp (mehrteilig) |
| **Komplexität** | **MITTEL** (30 Min). Änderung in 1 Datei, 15 Zeilen Code. |

**Code-Skizze:**
```python
# In whatsapp_webhook.py, run_audio() erweitern:
async def run_audio():
    # Schritt 1: Transkription via Gemini (existiert)
    result = await process_whatsapp_audio(audio_msg, sender)
    
    # Schritt 2: Transkript/Analyse an OMEGA_ATTRACTOR weiterleiten
    from src.network.openclaw_client import send_message_with_context, is_configured
    oc_response = None
    if is_configured():
        ok, oc_response = send_message_with_context(
            f"WhatsApp-Sprachnachricht von {sender}:\n{result}",
            agent_id="main", user=sender, timeout=30.0
        )
        if not ok:
            oc_response = None
    
    # Schritt 3: Antwort an Sender (mit OC-Kontext wenn vorhanden)
    reply = f"[CORE] {result}"
    if oc_response:
        reply += f"\n\n[OMEGA_ATTRACTOR] {oc_response}"
    ha_client.send_whatsapp(to_number=sender, text=reply)
```

### Lücke 3: Audio zurück (TTS) – OC-Antwort → ElevenLabs → WhatsApp/Minis

| Feld | Wert |
|---|---|
| **Lücke** | OMEGA_ATTRACTOR-Antworten werden nur als Text zurückgeliefert. Kein Pfad existiert, der OC-Antworten zu ElevenLabs-TTS wandelt und als Audio per WhatsApp sendet oder lokal abspielt. `e2e_event_to_tts.py` macht Event→OC→TTS, aber nur als Standalone-Skript (nicht in der WhatsApp-Pipeline). |
| **Warum jetzt nicht** | `elevenlabs_tts.py` ist voll funktional (API-Key gesetzt, 14 Voice-Rollen konfiguriert). `e2e_event_to_tts.py` beweist den Pfad OC→TTS. Aber: die WhatsApp-Pipeline nutzt TTS nicht und HA hat keine native Audio-Sende-Funktion über WhatsApp-Baileys. |
| **Harte Grenze?** | **Teilweise Ja** für WhatsApp-Audio-Rücksendung: Baileys-Integration auf HA-Addon-Ebene unterstützt `sendMessage` mit Text, aber Audio-Upload erfordert Baileys `sendMessage` mit Audio-Buffer – das HA-Addon muss das unterstützen. Für **lokale Mini-Lautsprecher**: **Nein** (Noch-nicht) – `speak_text(play=True)` funktioniert auf 4D_RESONATOR (CORE) (Windows `os.startfile`). |
| **Konkrete Lösung** | **Phase A (sofort, kein Blocker):** OC-Antwort → ElevenLabs TTS → Lokale Wiedergabe auf 4D_RESONATOR (CORE) (existiert in `autonomous_loop.py`). In WhatsApp-Pipeline einbauen: nach OC-Antwort `speak_text(oc_response, role_name="atlas_dialog", play=True)`. |
| | **Phase B (WhatsApp Audio-Rücksendung):** 1. TTS-MP3 erzeugen via `speak_text()`. 2. MP3 über HA-Addon als Audio-Nachricht an WhatsApp senden – erfordert Check ob Baileys-Addon `sendMessage({audio: buffer})` unterstützt. Falls ja: `ha_client.send_whatsapp_audio(to_number, mp3_path)` implementieren. Falls nein: MP3 als Document senden (Baileys unterstützt Document-Messages). |
| | **Phase C (Mini-Speaker):** HA `media_player.play_media` Service auf `media_player.mini_*` mit der TTS-MP3 URL. 4D_RESONATOR (CORE) stellt MP3 per API bereit, HA spielt auf Mini ab. |
| **Komplexität** | **Phase A: NIEDRIG** (15 Min, 5 Zeilen). **Phase B: MITTEL** (1-2h, HA-Addon-API prüfen). **Phase C: NIEDRIG** (30 Min, HA-Service-Call). |

### Lücke 4: Vision → Snapshot → Gemini Vision lokal → Beschreibung an OC

| Feld | Wert |
|---|---|
| **Lücke** | `vision_analysis.py` sendet Snapshot als Base64 an OMEGA_ATTRACTOR – aber OMEGA_ATTRACTOR auf dem VPS hat kein Gemini-Vision-Modell. Das B64-Bild wird als Text in JSON geschickt, OC kann damit nichts anfangen (kein Multimodal-LLM auf VPS). |
| **Warum jetzt nicht** | Architektur-Fehlentscheidung: Das Bild sollte LOKAL (4D_RESONATOR (CORE)) von Gemini Vision analysiert werden, und nur die TEXT-Beschreibung an OC gehen. Stattdessen wird das rohe Bild an OC geschickt. |
| **Harte Grenze?** | **Nein** (Noch-nicht). Gemini Vision (API-Key vorhanden), Kamera-Snapshot (go2rtc konfiguriert), OC-Client (funktional). Nur die Pipeline-Reihenfolge ist falsch. |
| **Konkrete Lösung** | `vision_analysis.py` umbauen: |
| | 1. Snapshot holen (existiert: `get_snapshot()`) |
| | 2. **LOKAL** an Gemini Vision senden (neuer Schritt): `genai.Client` mit `GEMINI_API_KEY`, Bild als `Part`, Prompt "Beschreibe was du siehst" |
| | 3. Gemini-Textantwort (Beschreibung) an OMEGA_ATTRACTOR senden (existiert: `send_event_to_oc_brain()`) – OHNE Base64, nur Text |
| | 4. OMEGA_ATTRACTOR erhält kontextualisierte Bildbeschreibung und kann darauf reagieren |
| **Komplexität** | **MITTEL** (45 Min). Hauptarbeit: Gemini Vision Aufruf in `vision_analysis.py` einfügen. |

**Code-Skizze:**
```python
# vision_analysis.py – umgebaut
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
VISION_MODEL = os.getenv("BRIO_VISION_MODEL", "gemini-3.1-pro-preview")

def analyze_vision(stream_name=None, prefer_scout_mx=True):
    ok, data, snapshot_source = get_snapshot(stream_name, prefer_source=prefer)
    if not ok:
        return False

    # LOKAL: Gemini Vision analysiert das Bild
    response = client.models.generate_content(
        model=VISION_MODEL,
        contents=[
            types.Part.from_bytes(data=data, mime_type="image/jpeg"),
            "Beschreibe was du auf diesem Bild siehst. Achte auf Personen oder Veränderungen."
        ],
        config=types.GenerateContentConfig(temperature=0.2)
    )
    description = response.text

    # NUR TEXT an OMEGA_ATTRACTOR (kein Base64 mehr)
    event = {
        "source": "dreadnought",
        "node_id": "pc-vision",
        "event_type": "vision_analysis",
        "data": {
            "description": description,
            "snapshot_source": snapshot_source,
        }
    }
    success, oc_response = send_event_to_oc_brain(event)
    return oc_response if success else None
```

### Lücke 5: WhatsApp-Audio umgeht OC – Pipeline ändern

| Feld | Wert |
|---|---|
| **Lücke** | Gesamte WhatsApp-Text-Pipeline umgeht OC ebenfalls. In `whatsapp_webhook.py`: Text-Triage → `atlas_llm.run_triage()` → HA-Command ODER `atlas_llm.invoke_heavy_reasoning()` → Antwort direkt zurück. OMEGA_ATTRACTOR wird NIRGENDS in der Text-Pipeline gerufen. Audio-Pipeline (Lücke 2) geht ebenfalls direkt Gemini→WhatsApp. |
| **Warum jetzt nicht** | Die WhatsApp-Pipeline wurde vor der OC-Integration gebaut. `atlas_llm` (lokales Gemini/Ollama) war der einzige Reasoning-Pfad. OMEGA_ATTRACTOR als zentrales Gehirn war noch nicht online. |
| **Harte Grenze?** | **Nein** (Noch-nicht). Alle Bausteine sind da. |
| **Konkrete Lösung** | WhatsApp-Pipeline-Refactor in 3 Stufen: |
| | **Stufe 1 – OC als Parallel-Empfänger (SOFORT, non-breaking):** Jede eingehende WhatsApp-Nachricht (Text + Audio-Transkript) wird ZUSÄTZLICH an OMEGA_ATTRACTOR gesendet via `send_message_with_context()`. Die aktuelle Antwort-Pipeline bleibt intakt. OC lernt mit, kann aber noch nicht antworten. |
| | **Stufe 2 – OC als primärer Reasoner (NÄCHSTER SCHRITT):** `@Core`-Nachrichten mit `intent == "deep_reasoning"` oder `"chat"` gehen an OMEGA_ATTRACTOR statt an `atlas_llm.invoke_heavy_reasoning()`. OC-Antwort zurück an WhatsApp. `atlas_llm` wird Fallback. |
| | **Stufe 3 – Vollautonomer OC-Loop:** OMEGA_ATTRACTOR wird alleiniger Reasoner. Lokales `atlas_llm` nur noch für Triage (intent detection) und als Offline-Fallback. OC entscheidet, OC antwortet, OC steuert HA über CORE-API. |
| **Komplexität** | **Stufe 1: NIEDRIG** (20 Min, ~10 Zeilen). **Stufe 2: MITTEL** (1h). **Stufe 3: HOCH** (halber Tag, Architektur-Entscheidung). |

---

## 2. Abhängigkeitsmatrix

```
Lücke 1 (OC Health-Check)
   ↓ muss zuerst
Lücke 2 (Audio→OC)  ──┐
Lücke 4 (Vision→OC) ──┤── alle brauchen OC online
Lücke 5 (WA Text→OC)──┘
   ↓ dann
Lücke 3 (TTS zurück) ── braucht OC-Antwort als Input
```

---

## 3. Priorisierter Aktionsplan

### PHASE 1: OC ONLINE BRINGEN (heute, 15 Min)

| # | Aktion | Befehl/Datei | Dauer |
|---|---|---|---|
| 1.1 | SSH auf VPS, Container-Status prüfen | `ssh root@187.77.68.250 "docker ps"` | 2 Min |
| 1.2 | Falls Container nicht laufen: Netzwerk + Compose starten | `docker network create atlas_net; cd /opt/core-core/docker/agi-state && docker compose up -d` | 5 Min |
| 1.3 | Gateway-Health von 4D_RESONATOR (CORE) testen | `python -c "from src.network.openclaw_client import check_gateway; print(check_gateway())"` | 1 Min |
| 1.4 | OC-Channel-Status über API testen | `curl http://localhost:8000/api/oc/status` (CORE API muss laufen) | 1 Min |
| 1.5 | Testmessage senden | `python -c "from src.network.openclaw_client import send_message_to_agent; print(send_message_to_agent('Ping – CORE Integrationstest'))"` | 2 Min |

### PHASE 2: AUDIO-PIPELINE INTEGRIEREN (heute, 30 Min)

| # | Aktion | Datei | Dauer |
|---|---|---|---|
| 2.1 | `whatsapp_webhook.py` → `run_audio()` erweitern: Transkript an OC senden | `src/api/routes/whatsapp_webhook.py` | 15 Min |
| 2.2 | TTS-Rückantwort (lokal) einfügen: `speak_text(oc_response)` | `src/api/routes/whatsapp_webhook.py` | 10 Min |
| 2.3 | E2E-Test: Sprachnachricht senden, OC-Antwort prüfen | Manuell via WhatsApp | 5 Min |

### PHASE 3: VISION-PIPELINE REPARIEREN (heute, 45 Min)

| # | Aktion | Datei | Dauer |
|---|---|---|---|
| 3.1 | `vision_analysis.py` umbauen: lokale Gemini-Vision-Analyse VOR OC-Send | `src/scripts/vision_analysis.py` | 30 Min |
| 3.2 | Base64-Payload aus Event entfernen, nur Text-Beschreibung senden | `src/scripts/vision_analysis.py` | 5 Min |
| 3.3 | Test: Snapshot → Gemini → Text → OC | `python src/scripts/vision_analysis.py` | 10 Min |

### PHASE 4: WHATSAPP-TEXT-PIPELINE INTEGRIEREN (morgen, 1-2h)

| # | Aktion | Datei | Dauer |
|---|---|---|---|
| 4.1 | Stufe 1: OC als Parallel-Empfänger für alle `@Core`-Nachrichten | `src/api/routes/whatsapp_webhook.py` | 20 Min |
| 4.2 | Stufe 2: `deep_reasoning`/`chat` Intent → OMEGA_ATTRACTOR statt `atlas_llm` | `src/api/routes/whatsapp_webhook.py` | 40 Min |
| 4.3 | Fallback-Logik: Wenn OC offline → `atlas_llm` als Backup | `src/api/routes/whatsapp_webhook.py` | 20 Min |
| 4.4 | E2E-Test: `@Core was ist der Sinn des Lebens?` → OC-Antwort in WhatsApp | Manuell | 10 Min |

### PHASE 5: TTS-RÜCKKANAL KOMPLETTIEREN (diese Woche)

| # | Aktion | Datei | Dauer |
|---|---|---|---|
| 5.1 | Phase A: Lokale TTS-Wiedergabe für OC-Antworten (4D_RESONATOR (CORE) Speaker) | `src/services/autonomous_loop.py` | 15 Min |
| 5.2 | Phase B: HA-Addon prüfen ob Baileys Audio-Send unterstützt | HA Addon-Doku | 30 Min |
| 5.3 | Phase B: `ha_client.send_whatsapp_audio()` implementieren | `src/network/ha_client.py` | 1h |
| 5.4 | Phase C: HA `media_player.play_media` für Minis | HA Automation | 30 Min |

---

## 4. Betroffene Dateien (Änderungs-Manifest)

| Datei | Änderungstyp | Phase |
|---|---|---|
| `src/api/routes/whatsapp_webhook.py` | **ERWEITERN** – OC-Integration in Audio + Text Pipeline | 2, 4 |
| `src/scripts/vision_analysis.py` | **UMBAUEN** – Gemini Vision lokal, nur Text an OC | 3 |
| `src/services/autonomous_loop.py` | **ERWEITERN** – TTS-Rückantwort für OC-Responses | 5 |
| `src/network/ha_client.py` | **ERWEITERN** – `send_whatsapp_audio()` Methode | 5 |
| `src/network/openclaw_client.py` | **KEINE ÄNDERUNG** – ist vollständig | - |
| `src/voice/elevenlabs_tts.py` | **KEINE ÄNDERUNG** – ist vollständig | - |
| `src/ai/whatsapp_audio_processor.py` | **KEINE ÄNDERUNG** – Transkription funktioniert | - |
| `src/config/voice_config.py` | **KEINE ÄNDERUNG** – 14 Rollen konfiguriert | - |

---

## 5. Risiken und Mitigationen

| Risiko | Wahrscheinlichkeit | Mitigation |
|---|---|---|
| OC-Container auf VPS nicht gestartet / crashed | MITTEL | Docker `restart: unless-stopped` ist gesetzt. Bei Crash: `docker compose logs` prüfen, neu starten. |
| Gateway-Token ungültig / abgelaufen | NIEDRIG | Token ist statisch konfiguriert (`ykKqxC...`). Bei 401: neuen Token generieren. |
| Gemini-Vision-Quota erschöpft | NIEDRIG | Fallback-Modell `BRIO_VISION_FALLBACK` ist konfiguriert. Bei Rate-Limit: Throttling einbauen. |
| WhatsApp-Baileys Audio-Send nicht unterstützt | MITTEL | Fallback: MP3 als Document-Attachment senden, oder Text-only-Modus. |
| Latenz OMEGA_ATTRACTOR > 30s | MITTEL | Timeout in `openclaw_client.py` ist 30s. WhatsApp-Webhook gibt sofort 202 zurück, Antwort kommt async. |

---

## 6. Zusammenfassung

**KERNAUSSAGE:** OCBrain ist **konfiguriert und erreichbar**. Die .env-Variablen sind NICHT das Problem. Die fünf Lücken sind reine **Software-Integrations-Lücken** – kein einziger physikalischer Blocker.

| Lücke | Blocker? | Lösung | Zeit |
|---|---|---|---|
| 1. OC offline | Nein | Docker-Container starten/prüfen | 15 Min |
| 2. Audio → OC | Nein | `whatsapp_webhook.py` erweitern | 30 Min |
| 3. TTS zurück | Teilweise (WA-Audio) | Phase A sofort, Phase B prüfen | 15 Min – 2h |
| 4. Vision → OC | Nein | `vision_analysis.py` umbauen | 45 Min |
| 5. WA umgeht OC | Nein | Stufenweise OC-Integration | 1.5h |

**Gesamtaufwand bis OC-Vollintegration: ~4-5 Stunden.**  
**Davon heute machbar (Phase 1-3): ~1.5 Stunden.**

---

*Erstellt: 2026-03-01 | Produzent Schicht 3 | Evolutionsprinzip*
