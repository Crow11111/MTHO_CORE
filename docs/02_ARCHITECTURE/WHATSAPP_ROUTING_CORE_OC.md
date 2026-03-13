<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# WhatsApp-Routing: @Core und @OC

Einheitliche Regeln für CORE/Scout und OC in WhatsApp. Beide folgen diesem Modell.

---

## Adressierung

| Präfix / Adressat | Wer reagiert | Format der Antwort |
|-------------------|--------------|---------------------|
| **@Core** (am Anfang) | CORE / Scout | [CORE] bzw. [Scout] |
| **@OC** (am Anfang) | Nur OC | [OC] oder @OC |

- **Nur einer adressiert** → nur der reagiert. Nachricht mit @OC am Anfang geht nur an OC (CORE antwortet normalerweise nicht). Nachricht mit @Core am Anfang wird von CORE/Scout verarbeitet (OC reagiert darauf normalerweise nicht).
- **@Core am Anfang und @OC später** → Teil für den anderen oder beide relevant; CORE verarbeitet (Antwort [CORE]/[Scout]); OC kann den Teil nach @OC für sich nutzen.

---

## Bedenken-Pflicht (gilt in beide Richtungen)

**Regel:** Wenn nur der **andere** adressiert ist, du aber **eklatante Bedenken oder Einwände** hast, bist du **verpflichtet**, dich trotzdem zu melden.

- **Nur @OC adressiert** → CORE antwortet standardmäßig nicht. **Ausnahme:** CORE hat eklatante Bedenken → CORE **muss** sich einmischen (Antwort mit [CORE]).
- **Nur @CORE adressiert** → OC antwortet standardmäßig nicht. **Ausnahme:** OC hat eklatante Bedenken → OC **muss** sich einmischen (Antwort mit [OC]).

**Warum?** Sicherheit und Aufsicht. CORE ist die letzte Instanz (z. B. Steuerung, System); wenn nur mit OC gesprochen wird und etwas Kritisches passiert, muss CORE eingreifen können. Umgekehrt: Wenn nur CORE adressiert ist und OC etwas Wichtiges (in seinem Kontext) erkennt, muss OC sich melden. So überwiegt die Pflicht zur Klärung die reine Adressaten-Regel.

---

## CORE-Seite (Webhook / Skripte)

- Reagieren **nur**, wenn die Nachricht **mit @Core beginnt** (case-insensitiv). Sonst standardmäßig keine Antwort.
- Wenn die Nachricht **mit @OC beginnt** → standardmäßig ignorieren (ist für OC). **Ausnahme:** Eklatante Bedenken → trotzdem antworten mit [CORE]/[Scout].
- @Core-Prefix vor der Verarbeitung abziehen; Antworten immer mit **[CORE]** oder **[Scout]** beginnen (Sender-Identifikation).

---

## OC-Seite (Prozedere für OpenClaw)

- **Wenn eine Nachricht explizit mit @CORE (oder anderem ID/Name) beginnt:** Darauf brauchst du **nicht** zu reagieren (ist für CORE). **Ausnahme:** Eklatante Bedenken → trotzdem melden.
- **Sonst:** Wenn in der Nachricht an **späterer Stelle @OC** vorkommt, ist (diese Passage) für dich – darauf reagieren.
- **Wenn du nicht adressiert wirst, aber eklatante Bedenken/Einwände hast:** Du bist **verpflichtet**, das trotzdem zu melden.
- Antworten mit **[OC]** oder „@OC“, damit die Quelle klar ist.

---

## Dokumentation / Implementierung

- In Core-Logik/Webhook/Skript: Routing wie oben; [CORE]/[Scout] in allen ausgehenden WhatsApp-Antworten.
- OC: gleiche Routing-Logik und [OC]-Format in den Dokumenten und in der OC-Konfiguration ergänzen/anpassen.

---

## Offene Punkte

- **@-Präfix nur Zwischenlösung:** Das Reagieren nur bei @Core/@OC dient dazu, dass z. B. Nachrichten von der Schwester oder anderen Kontakten **nicht** automatisch etwas auslösen. Kein Dauerzustand.
- **Eigener Dienst:** Die Trigger-/Routing-Logik (wer reagiert wann) soll perspektivisch in einen **eigenen Dienst** ausgelagert werden – wird auf jeden Fall noch geplant/umgesetzt.
- **Abstimmung CORE ↔ OC ↔ Dev-Agent:** Gemeinsamer Plan: **docs/WHATSAPP_TRIGGER_UND_ADRESSIERUNG_PLAN.md**. OC erreichst du mit **einer** WhatsApp-Nachricht, die mit **@OC** beginnt (kein separates System nötig).
- **HA auf Hostinger (optional):** Ein-Klick-Installation; dann HA + OC auf einem Bus. Siehe Plan-Doc Abschnitt „HA auf Hostinger“.
