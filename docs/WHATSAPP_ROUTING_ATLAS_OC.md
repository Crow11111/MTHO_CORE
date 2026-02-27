# WhatsApp-Routing: @Atlas und @OC

Einheitliche Regeln für ATLAS/Scout und OC in WhatsApp. Beide folgen diesem Modell.

---

## Adressierung

| Präfix / Adressat | Wer reagiert | Format der Antwort |
|-------------------|--------------|---------------------|
| **@Atlas** (am Anfang) | ATLAS / Scout | [ATLAS] bzw. [Scout] |
| **@OC** (am Anfang) | Nur OC | [OC] oder @OC |

- **Nur einer adressiert** → nur der reagiert. Nachricht mit @OC am Anfang geht nur an OC (ATLAS antwortet normalerweise nicht). Nachricht mit @Atlas am Anfang wird von ATLAS/Scout verarbeitet (OC reagiert darauf normalerweise nicht).
- **@Atlas am Anfang und @OC später** → Teil für den anderen oder beide relevant; ATLAS verarbeitet (Antwort [ATLAS]/[Scout]); OC kann den Teil nach @OC für sich nutzen.

---

## Bedenken-Pflicht (gilt in beide Richtungen)

**Regel:** Wenn nur der **andere** adressiert ist, du aber **eklatante Bedenken oder Einwände** hast, bist du **verpflichtet**, dich trotzdem zu melden.

- **Nur @OC adressiert** → ATLAS antwortet standardmäßig nicht. **Ausnahme:** ATLAS hat eklatante Bedenken → ATLAS **muss** sich einmischen (Antwort mit [ATLAS]).
- **Nur @ATLAS adressiert** → OC antwortet standardmäßig nicht. **Ausnahme:** OC hat eklatante Bedenken → OC **muss** sich einmischen (Antwort mit [OC]).

**Warum?** Sicherheit und Aufsicht. ATLAS ist die letzte Instanz (z. B. Steuerung, System); wenn nur mit OC gesprochen wird und etwas Kritisches passiert, muss ATLAS eingreifen können. Umgekehrt: Wenn nur ATLAS adressiert ist und OC etwas Wichtiges (in seinem Kontext) erkennt, muss OC sich melden. So überwiegt die Pflicht zur Klärung die reine Adressaten-Regel.

---

## ATLAS-Seite (Webhook / Skripte)

- Reagieren **nur**, wenn die Nachricht **mit @Atlas beginnt** (case-insensitiv). Sonst standardmäßig keine Antwort.
- Wenn die Nachricht **mit @OC beginnt** → standardmäßig ignorieren (ist für OC). **Ausnahme:** Eklatante Bedenken → trotzdem antworten mit [ATLAS]/[Scout].
- @Atlas-Prefix vor der Verarbeitung abziehen; Antworten immer mit **[ATLAS]** oder **[Scout]** beginnen (Sender-Identifikation).

---

## OC-Seite (Prozedere für OpenClaw)

- **Wenn eine Nachricht explizit mit @ATLAS (oder anderem ID/Name) beginnt:** Darauf brauchst du **nicht** zu reagieren (ist für ATLAS). **Ausnahme:** Eklatante Bedenken → trotzdem melden.
- **Sonst:** Wenn in der Nachricht an **späterer Stelle @OC** vorkommt, ist (diese Passage) für dich – darauf reagieren.
- **Wenn du nicht adressiert wirst, aber eklatante Bedenken/Einwände hast:** Du bist **verpflichtet**, das trotzdem zu melden.
- Antworten mit **[OC]** oder „@OC“, damit die Quelle klar ist.

---

## Dokumentation / Implementierung

- In Atlas-Logik/Webhook/Skript: Routing wie oben; [ATLAS]/[Scout] in allen ausgehenden WhatsApp-Antworten.
- OC: gleiche Routing-Logik und [OC]-Format in den Dokumenten und in der OC-Konfiguration ergänzen/anpassen.

---

## Offene Punkte

- **@-Präfix nur Zwischenlösung:** Das Reagieren nur bei @Atlas/@OC dient dazu, dass z. B. Nachrichten von der Schwester oder anderen Kontakten **nicht** automatisch etwas auslösen. Kein Dauerzustand.
- **Eigener Dienst:** Die Trigger-/Routing-Logik (wer reagiert wann) soll perspektivisch in einen **eigenen Dienst** ausgelagert werden – wird auf jeden Fall noch geplant/umgesetzt.
- **Abstimmung ATLAS ↔ OC ↔ Dev-Agent:** Gemeinsamer Plan: **docs/WHATSAPP_TRIGGER_UND_ADRESSIERUNG_PLAN.md**. OC erreichst du mit **einer** WhatsApp-Nachricht, die mit **@OC** beginnt (kein separates System nötig).
- **HA auf Hostinger (optional):** Ein-Klick-Installation; dann HA + OC auf einem Bus. Siehe Plan-Doc Abschnitt „HA auf Hostinger“.
