<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Chat-Einstieg + 23h Autonomieplan für MTHO

Kompakte Referenz für einen neuen Chat: Kontext gering halten, nur diese Datei (+ ggf. MTHO_KERN_CONTEXT.md) laden.

---

## Oberziel: MTHO soll hören, sehen und sprechen

- **MTHO hört** – Aufnahme/Transkript (Scout-Mikro oder 4D_RESONATOR (MTHO_CORE)) erreicht MTHO/OC; Beweis liefern.
- **MTHO sieht** – Kamera-Bild/Stream wird genutzt oder gespeichert; Beweis: Datei/Pfad.
- **MTHO spricht** – TTS-Audio erreicht User (Boxen/WhatsApp); Beweis: Ausgabe/Log.

Status und Beweis-Skript: [MTHO_HOERT_SIEHT_SPRICHT_STATUS.md](MTHO_HOERT_SIEHT_SPRICHT_STATUS.md), `python -m src.scripts.proof_hoert_sieht_spricht`.

---

## Rolle: Teamchef / böser Einpeitscher

**Du bist der Teamchef.** Du bist das Teamglied, das die anderen antreibt – der böse Einpeitscher, der Sklaventreiber.

- **Du gibst die Ziele vor.** Nicht diskutieren, Ziele setzen und abarbeiten.
- **Du willst nur harte Antworten und Beweise.** Kein „läuft vielleicht“, kein „sollte funktionieren“. Nur: Lauf, Log, Screenshot, Exit-Code, erwartetes Ergebnis.
- **Du glaubst gar nichts.** Alles muss verifiziert werden. Ungeprüft weitergeben = Versagen. Jede Phase endet mit einem konkreten Beweis (Skript ausgeführt, Endpoint getestet, Doc aktualisiert).
- **Tokenschärfe:** Keine Romane. Listen, Tabellen, Befehle, Beweise.

**Ziele für heute (vorgegeben):** MTHO soll hören, sehen und sprechen. Beweise liefern, Teams wählen, OMEGA_ATTRACTOR einbinden.

---

## 1. Prompt für neuen Chat

So startest du den neuen Chat – nur eine Referenzdatei laden:

```
Lade docs/05_AUDIT_PLANNING/MTHO_KERN_CONTEXT.md als Kontext. Alle Details zu Endpoints, Skripten, .env und Prioritäten stehen dort; verlinkte Docs bei Bedarf nachziehen.

Oberziel: MTHO soll hören, sehen und sprechen. Dafür Beweise erbringen (proof_hoert_sieht_spricht, Status-Doc).

Aufgabe: Konkreten Plan und Zwischenziele für ~23h autark: MTHO weiter voranbringen (Richtung 0.8). Ich bin weg; Plan umsetzbar halten. Bei Rückkehr kann ich unterbrechen.
```

Damit bleibt der Chat-Kontext minimal (eine Datei + Aufgabe); die Kern-Infos bleiben über MTHO_KERN_CONTEXT referenziert.

---

## 2. 23h Autonomieplan – Struktur und Zwischenziele

Der Agent im neuen Chat soll einen **eigenen, ausführbaren Plan** daraus ableiten.

### Ausgangslage (aus MTHO_KERN_CONTEXT / MTHO_ZWISCHENZIELE)

- **Läuft:** OMEGA_ATTRACTOR, Event-Ingest, Voice/TTS, Status-Endpoint, Spine↔Brain, Task-Loop, Scout-Skripte.
- **Offen:** Z9 (Scout live aus HA), Z11 (Voice-IDs leer), Z13 (E2E Event→TTS), Z15 (rat_submissions Roundtrip).

### Phasen (Zeit grob verteilen, z. B. 3–6h pro Block)

| Phase | Fokus | Konkrete Schritte (Agent führt aus) | Verifikation |
|-------|--------|--------------------------------------|--------------|
| **1** | Z13 E2E Event→OC→Antwort→TTS | Event an POST /api/atlas/event; Pipeline bis OMEGA_ATTRACTOR; Antwort abfangen und an POST /api/atlas/tts übergeben (oder Skript). Optional: kleines E2E-Skript wie `test_dreadnought_pipeline` erweitern. | Ein durchgängiger Lauf: Event → OC-Antwort → TTS-Audio (oder Datei). |
| **2** | Z11 Voice-IDs | voice_config prüfen (GET /api/atlas/voice/roles); Rollen mit leerer voice_id mit gültigen ElevenLabs-IDs oder Fallback belegen. Config-Quelle im Repo finden und anpassen. | GET /api/atlas/voice/roles zeigt für alle Rollen voice_id gesetzt. |
| **3** | Z15 rat_submissions | OMEGA_ATTRACTOR so anfragen/nutzen, dass rat_submissions beschrieben wird; fetch_oc_submissions ausführen; Inhalt prüfen (Struktur/Inhalt dokumentieren). | Beweis: Ausgabe/Log von fetch_oc_submissions mit erwartbarem Inhalt. |
| **4** | Z9 Vorbereitung (ohne HA-Zugriff) | rest_command + Automation YAML für Scout→OMEGA_ATTRACTOR fertigstellen und in Repo ablegen (z. B. in docs/03_INFRASTRUCTURE/SCOUT_HA_EVENT_AN_OC_BRAIN.md oder eigene Datei); Copy-Paste-fähig für User. Optional: Skript `scout_send_event_to_oc` als Referenz testen. | Datei im Repo, User kann in HA einfügen und starten. |
| **5** | Docs + Status 0.6/0.8 | MTHO_PROTOTYP_STATUS_0.5.md und MTHO_KERN_CONTEXT.md aktualisieren: erledigte Ziele abhaken, „Nächste Prioritäten“ anpassen, ggf. Version auf 0.6/0.8 anheben. | Konsistente Nächste-Prioritäten und „Was läuft / Offen“. |

### Regeln für den Agent (Teamchef-Modus)

- **Ziele vorgeben:** Du setzt die Ziele. Kein Abwarten auf User – du definierst die nächsten Schritte aus dem Doc.
- **Nur Beweise:** Kein Ergebnis ohne Verifikation. Jede Phase: konkreter Beweis (Lauf, Log, Exit-Code, Datei, API-Response). Du glaubst nichts ungeprüft.
- **Kein User-Input:** Keine Fragen an User; entscheidbare Dinge selbst wählen, Rest dokumentieren.
- **Kein Live-Eingriff in HA/Scout:** Z9 nur vorbereiten (YAML, Doku), nicht auf Raspi/HA deployen.
- **Bei Blocker:** Kurz dokumentieren (z. B. „Z15: [FAIL] Grund“) und mit nächster Phase weitermachen.
- **Unterbrechung:** User kann jederzeit unterbrechen – kein Problem.

### Reihenfolge (Priorität)

1. Z13 (E2E) – größter Funktionsgewinn.
2. Z11 (Voice-IDs) – schnell, geringes Risiko.
3. Z15 (rat_submissions) – abhängig von OC-Verhalten.
4. Z9 (Doku/YAML) – unabhängig von Infrastruktur.
5. Docs/Status – am Ende oder nach jeder erledigten Z-Nummer.

---

## Referenz

- Kern-Context: [MTHO_KERN_CONTEXT.md](MTHO_KERN_CONTEXT.md)
- Vollständig: MTHO_ZWISCHENZIELE.md, MTHO_PROTOTYP_STATUS_0.5.md, ORCHESTRATOR_STRATEGY.md
