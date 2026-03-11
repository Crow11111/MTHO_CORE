<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# WhatsApp: Trigger & Adressierung – Plan (MTHO ↔ OC ↔ Dev-Agent)

**Ziel:** Sicherstellen, dass (1) Nachrichten **richtig adressiert** werden (wer reagiert), (2) **alles von allen gelesen** werden kann (Leserecht), (3) **ohne Trigger** (nicht von Marc oder von den Systemen) **keine Nachricht, die für Marc bestimmt war, systemisch beantwortet** wird – z. B. Schwester schreibt Marc, System antwortet nicht.

Abstimmung zwischen **MTHO** (Webhook/HA-Pfad), **OC** (OpenClaw) und **Dev-Agent** (Tests/Doku). Dieser Plan ist die gemeinsame Basis; OC und Dev-Agent können unten ergänzen.

---

## 1. Ausgangslage

| Kanal | Wer sieht was? | Risiko „falsch antworten“ |
|--------|----------------|----------------------------|
| **HA-Pfad (MTHO)** | **Alle** eingehenden Nachrichten in Marcs Account (Addon meldet jedes Event). Also: Schwester → Marc, Kollege → Marc, Marc → sich selbst, etc. | **Hoch:** Ohne Filter würde MTHO auf jede Nachricht antworten. |
| **OC (OpenClaw)** | Nur Nachrichten, die **an Marcs Nummer** gehen und **von erlaubten Absendern** kommen (`allowFrom`). Aktuell z. B. nur Marcs eigene Nummer (Nachrichten „von mir an mich“). | **Geringer:** OC sieht z. B. Schwester→Marc gar nicht, wenn `allowFrom` nur Marc enthält. |

**Kernproblem HA-Pfad:** Das Addon liefert **jede** eingehende Nachricht an MTHO. Es gibt keine „zweite Nummer“ – alles läuft über Marcs Account. Daher: **Trigger nötig**, damit nur gewollte Nachrichten eine System-Antwort auslösen (aktuell: @Atlas / @OC).

---

## 2. Anforderungen (kurz)

- **Adressierung:** @Atlas → MTHO/Scout; @OC → OC. Nur der Adressierte antwortet (plus Bedenken-Pflicht). Siehe [WHATSAPP_ROUTING_MTHO_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_MTHO_OC.md).
- **Alles lesen:** Beide Systeme dürfen Nachrichten lesen können (für Kontext/Bedenken); Lesen ≠ Antworten.
- **Keine systemische Antwort ohne Trigger:** Wenn eine Nachricht **für Marc persönlich** bestimmt ist (z. B. von der Schwester, ohne @Atlas/@OC), darf **kein** System (MTHO, OC) automatisch antworten. Trigger = explizite Ansprache (z. B. @Atlas, @OC) oder später: eigener Dienst / Allowlist.

---

## 3. Optionen für „sicher nur bei Trigger antworten“

### A) Trigger im Text (aktuell, Zwischenlösung)

- Nachricht **beginnt mit @Atlas** → MTHO darf antworten.
- Nachricht **beginnt mit @OC** → nur OC (MTHO ignoriert).
- Kein @-Präfix / anderer Absender ohne Trigger → **keine** System-Antwort.
- **Vorteil:** Einfach, sofort wirksam. **Nachteil:** Nutzer müssen das Präfix nutzen; kein Schutz, wenn jemand z. B. „@Atlas“ in einem normalen Satz schreibt (könnte man einschränken: nur am Anfang zählen).

### B) Allowlist Absender (HA / MTHO)

- **Vor** dem Aufruf des MTHO-Webhooks: Nur wenn `remoteJid` / Absender in einer erlaubten Liste steht (z. B. nur Marcs Nummer beim Schreiben von anderem Gerät), wird der Webhook aufgerufen. Alle anderen Nachrichten werden nicht an MTHO weitergeleitet.
- **Vorteil:** Schwester/Kollegen lösen gar nichts aus. **Nachteil:** Du musst alle „erlaubten“ Nummern pflegen; Gäste/Second-Geräte müssen explizit drinstehen.

### C) Getrennte Nummern / Kanäle (OC-Dokumentation, erprobtes Verfahren)

- **Zwei Nummern:** Eine Nummer nur für „System“ (MTHO/OC), eine für privaten Chat. Nur Nachrichten an die System-Nummer werden verarbeitet. So sieht das System nie Chats, die nur für Marc bestimmt sind.
- **OC:** Nutzt bereits Konzepte wie `allowFrom`; eigenes Gateway = eigene Session, ggf. eigene Nummer. Ein bekanntes, erprobtes Vorgehen ist: **Klare Trennung nach Nummer** – z. B. nur eine bestimmte Nummer (oder Liste) darf den Agenten auslösen.
- **Vorteil:** Sauber getrennt, keine versehentlichen Antworten in Privatchats. **Nachteil:** Zweite Nummer/Account nötig; Aufwand für Setup.

### D) Eigener Dienst (geplant, siehe Offene Punkte)

- Trigger- und Routing-Logik in einen **eigenen Dienst** auslagern (zwischen HA-Event und MTHO/OC). Dieser Dienst entscheidet: Weiterleiten oder nicht, an wen, mit welchem Kontext.
- Ermöglicht später: Kombination aus Allowlist + Trigger + ggf. getrennte Kanäle an einer Stelle.

---

## 4. Wo steht wer?

- **MTHO (HA-Pfad):** Sieht alle Nachrichten, die ins Addon kommen. Reagiert nur bei @Atlas am Anfang (bzw. bei @OC am Anfang: nicht, außer Bedenken). Implementiert in `whatsapp_webhook.py`.
- **OC:** Sieht nur, was das OC-Gateway bekommt – abhängig von `allowFrom` und welcher Account mit dem Kanal verknüpft ist. Typischerweise nur Nachrichten **an Marcs Nummer von Marc** (andere Geräte) oder von explizit erlaubten Nummern. Vorschlag/erprobtes Procedere von OC (z. B. strikte Allowlist, getrennte Nummer) soll hier eingetragen werden.
- **Dev-Agent:** Kann Tests und Doku prüfen/ergänzen (z. B. „Trigger nur am Anfang“, Allowlist-Tests, E2E ohne falsche Antwort an Dritte).

---

## 5. Konkreter Plan (Schritte)

1. **Trigger-Regel beibehalten und dokumentieren**  
   @Atlas / @OC am Anfang; keine Antwort ohne Trigger. Doku: [WHATSAPP_ROUTING_MTHO_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_MTHO_OC.md). Bereits umgesetzt.

2. **OC: Erprobtes Procedere festhalten**  
   OC (oder Dev-Agent mit OC-Kontext) trägt ein: Welches Vorgehen für „sichere Adressierung / nur richtige Absender“ wird empfohlen? (z. B. nur `allowFrom` mit Marcs Nummer, oder eigene Nummer für Bot, oder Kombination mit Trigger.)

3. **HA optional: Allowlist vor Webhook**  
   Wenn gewünscht: In HA nur dann `rest_command.atlas_whatsapp_webhook` aufrufen, wenn Absender (`remoteJid`) in einer Liste erlaubter Nummern steht. Reduziert Last und Risiko; Trigger bleibt zweite Schicht.

4. **Eigener Dienst (später)**  
   Trigger- und Routing-Logik in eigenen Dienst auslagern; siehe [WHATSAPP_ROUTING_MTHO_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_MTHO_OC.md) – Offene Punkte.

5. **Tests / Checkliste (Dev-Agent)**  
   - Nachricht ohne Trigger (z. B. „Hallo“ von Test-Absender) → keine MTHO-/OC-Antwort.  
   - Nachricht mit @Atlas → MTHO antwortet mit [MTHO]/[Scout].  
   - Nachricht mit @OC → MTHO antwortet nicht (OC antwortet, wenn konfiguriert).  
   - Optional: Allowlist-Test (nur erlaubter Absender führt zu Webhook-Aufruf).

---

## 5b. Abstimmung auslösen (Trigger für OC und Dev-Agent)

Damit OC und Dev-Agent **wissen**, dass sie Abschnitt 6 bearbeiten sollen, gibt es zwei Wege – **ohne SSH** zum „Verbinden“, sondern per **Aufruf von Skripten**:

| Wen | Wie | Skript |
|-----|-----|--------|
| **OC** | Eine Nachricht mit der Aufgabe wird **per API** an das OpenClaw-Gateway geschickt (MTHO → OC). OC erhält sie im gleichen Kanal wie andere Eingaben und kann antworten oder eine Einreichung in `rat_submissions/` ablegen. | `python -m src.scripts.trigger_whatsapp_plan_oc` |
| **Dev-Agent** | Der Dev-Agent wird **lokal gestartet** mit Kontext (dieser Plan + dev_agent_whatsapp_context.md) und dem Auftrag, Abschnitt 6 (Dev-Agent-Teil) auszufüllen. Die Ausgabe wird in eine Datei geschrieben; du fügst sie danach in Abschnitt 6 ein oder nutzt sie als Vorlage. | `python -m src.scripts.trigger_whatsapp_plan_dev_agent` |

- **OC:** Kein SSH nötig – die Kommunikation läuft über die bestehende Gateway-API (`send_message_to_agent`). Das Skript sendet die Aufgabentexte (inkl. relevanter Plan-Auszüge) an den Agenten „main“. OC soll seine Antwort als **rat_submission** ablegen (topic z. B. „WhatsApp-Plan Abschnitt 6“); MTHO holt sie mit `fetch_oc_submissions` ab.
- **Dev-Agent:** Läuft auf deinem Rechner (Gemini/Claude). Das Skript ruft den Dev-Agent mit dem richtigen Prompt und den Kontextdateien auf und schreibt die Antwort nach `docs/WHATSAPP_PLAN_DEV_AGENT_ANTWORT.md`. Du kannst den Inhalt von dort in Abschnitt 6 kopieren oder die Datei als Referenz behalten.

**Ablauf, wenn du die Abstimmung starten willst:**  
1. Beide Skripte nacheinander (oder parallel) ausführen.  
2. OC-Antwort später aus `rat_submissions` holen (`python -m src.scripts.fetch_oc_submissions`) und in Abschnitt 6 eintragen.  
3. Dev-Agent-Antwort aus `docs/WHATSAPP_PLAN_DEV_AGENT_ANTWORT.md` in Abschnitt 6 eintragen.

### Probleme beheben (Gateway 405, Config, etc.)

- **Problem per WhatsApp an @OC adressieren:** Wenn etwas nicht funktioniert (z. B. API 405, Gateway antwortet nicht), das Problem **per WhatsApp mit @OC** schicken. OC prüft, ob er **von innen** (im Container/Workspace) oder per SSH etwas machen kann.
- **Wer führt aus:** Entweder **OC** (wenn er Zugriff hat) oder **MTHO** (z. B. Skript `enable_oc_responses_vps` per SSH vom Rechner aus). Ziel: dass es klappt.
- **Wenn es nicht klappt:** Gemeinsam eine **Alternative** nutzen:
  - **Einfachste Variante:** OC erreichst du, indem du **eine einzige WhatsApp-Nachricht** schickst, die **mit @OC beginnt**. Z. B.: „@OC Lies workspace/whatsapp_plan_task.md und fülle Abschnitt 6 aus; Antwort in rat_submissions (topic: WhatsApp-Plan Abschnitt 6).“ Kein separates System nötig – dieselbe WhatsApp, Nachricht mit @OC einleiten, fertig. (Optional: Nach dem Deploy der Task-Datei kann eine Automation diese eine Nachricht automatisch senden, z. B. HA whatsapp/send_message mit genau diesem Text an deine Nummer – dann fährt alles auf dem gleichen Bus.)
  - **Variante A (Task im Workspace):** Skript `deploy_whatsapp_plan_task_to_oc` legt die Datei auf dem VPS ab. Danach die **eine** WhatsApp mit @OC (siehe oben).
  - **Variante B:** Die **eine** WhatsApp mit @OC enthält die Aufgabentexte direkt (ohne workspace-Datei). OC antwortet im Chat oder legt rat_submission an.
  - **Variante C (Logikketten / Logikschalter in HA):** Siehe unten „Workaround: Logikschalter in HA“.

### Workaround: Logikschalter in HA (Logikketten)

Damit die Kommunikation mit OC per **Logikketten/Logikschalter** auslösbar ist (ohne Skript von Hand), bietet MTHO ein Endpoint, das API-Versuch und Fallback bündelt:

- **Endpoint:** `POST http://MTHO_IP:8000/api/oc/trigger_whatsapp_plan` (kein Body nötig).
- **Logik:** (1) Versuch, OC per API zu benachrichtigen. (2) Bei Fehler (z. B. 405) automatisch **Fallback:** Task-Datei per SSH in OCs Workspace legen und **eine WhatsApp** mit @OC an deine Nummer senden (über HA, wenn HASS_URL/HASS_TOKEN/WHATSAPP_TARGET_ID gesetzt). Dann sollte das Handy klingeln und OC die Nachricht sehen (gleicher Account). Sonst die Nachricht manuell schicken.

**Einbindung in HA (Beispiel):**

1. **rest_command** in HA anlegen (z. B. in `configuration.yaml` oder über UI):
   ```yaml
   rest_command:
     atlas_oc_trigger_whatsapp_plan:
       url: "http://DEINE_MTHO_IP:8000/api/oc/trigger_whatsapp_plan"
       method: POST
       content_type: "application/json"
   ```
2. **Logikschalter:** Einen Helper anlegen (Einstellungen → Geräte & Dienste → Helfer), z. B. **input_boolean** mit ID `oc_abstimmung_anfordern`.
3. **Automation:** Wenn `input_boolean.oc_abstimmung_anfordern` von aus auf an wechselt → Aktion `rest_command.atlas_oc_trigger_whatsapp_plan` ausführen. Optional: Schalter danach wieder ausschalten oder eine Benachrichtigung mit der Antwort (method, message) anzeigen.

Damit reicht es, den Schalter zu betätigen (oder eine Szene/Automation daran zu knüpfen); die Logikketten erledigen den Rest (API oder Fallback). Im Zweifel immer dieser Workaround nutzbar.

### HA auf Hostinger (optional): „Alle auf dem gleichen Bus“

**Frage:** Würde es viele Kommunikationsprobleme erleichtern, wenn auf dem Hostinger-Server **auch** eine HA-Instanz läuft? Dann wären HA, OC (OpenClaw) und ggf. ein schlanker MTHO-Proxy auf **einem** Host – alle auf dem **gleichen Bus** (gleiches Netz, localhost oder lokales LAN).

**Einschätzung:**
- **Abstimmungen, Trigger, Logikketten:** Für solche Abläufe sind Geschwindigkeit und Latenz **nicht** entscheidend. Ein gemeinsamer Bus (HA auf Hostinger) könnte vereinfachen: rest_command von HA zu OC oder zu einem lokalen Dienst, Automations alle auf einer Maschine, kein NAT/Firewall zwischen Scout-HA und Hostinger-OC.
- **Vorteile:** Eine zentrale HA-Instanz auf Hostinger könnte z. B. (1) OC und ggf. MTHO-Dienste per localhost/Inter-Container ansprechen, (2) WhatsApp-Addon oder -Integration an einem Ort bündeln, (3) Logikschalter und Abstimmungs-Automations ohne Umweg über den Scout/4D_RESONATOR (MTHO_CORE) betreiben.
- **Aufwand:** HA auf Hostinger ist eine **Ein-Klick-Installation** – der Einstieg ist gering. Danach: gleicher Bus für HA, OC und ggf. Dienste; Backup-Konzept und Wartung wie bei jeder zweiten Instanz zu bedenken.

**Fazit:** Option sinnvoll, wenn Kommunikationsprobleme (API 405, getrennte Netze) weiter stören. HA auf Hostinger per Ein-Klick – dann alle auf dem gleichen Bus; für Abstimmungen und Trigger ist Latenz unkritisch.

---

## 6. Abstimmung OC / Dev-Agent (Platzhalter)

**OC:** Bitte hier eintragen (oder Verweis auf Stammdokument/Config):
- Empfohlenes Procedere für „nur richtige Absender / unterschiedliche Nummern“ (z. B. `allowFrom`, getrennte Nummer, Kombination mit @OC).
- Ob OC aktuell nur Nachrichten „von Marc an Marc“ sieht und wie das mit der Trigger-Regel zusammenspielt.

**Dev-Agent:** (eingetragen nach Lauf von `trigger_whatsapp_plan_dev_agent`)

- **Konkrete Tests:** (1) Webhook & Trigger: `tests/test_whatsapp_webhook.py` mit TestClient – Cases: „Hallo“ → ignoriert, „@Atlas Ping“ → Verarbeitung, „@OC Ping“ → MTHO antwortet nicht. (2) E2E HA: `src/scripts/test_whatsapp_e2e_ha.py`. (3) OpenClaw E2E: `src/scripts/test_openclaw_e2e.py` mit openclaw_client. (4) Optional Allowlist: `tests/test_whatsapp_allowlist.py` bei Umsetzung.
- **Doku vs. Code:** Doku stimmig. Lücke: Bei @OC ist die Bedenken-Pflicht im Webhook noch nicht umgesetzt (@OC wird nur ignoriert). Vorschlag: Bei @OC asynchrone Bedenken-Prüfung im Hintergrund starten, Webhook sofort beenden. Details siehe `docs/WHATSAPP_PLAN_DEV_AGENT_ANTWORT.md`.

---

## 7. Referenzen

- [WHATSAPP_ROUTING_MTHO_OC.md](../02_ARCHITECTURE/WHATSAPP_ROUTING_MTHO_OC.md) – Routing, Bedenken-Pflicht, Offene Punkte
- [WHATSAPP_E2E_HA_SETUP.md](../03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md) – HA-Setup, Automation, 2.1 Routing
- [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md) – OC vs. HA-Pfad, allowFrom
- [DEV_AGENT_UND_SCHNITTSTELLEN.md](../02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md) – Netzarchitektur, Addon, OC
- `src/api/routes/whatsapp_webhook.py` – MTHO-Trigger-Logik (@Atlas / @OC am Anfang)
- **Trigger-Skripte:** `src/scripts/trigger_whatsapp_plan_oc.py` (OC per API), `src/scripts/trigger_whatsapp_plan_dev_agent.py` (Dev-Agent lokal)
- **Alternative wenn API 405:** `src/scripts/deploy_whatsapp_plan_task_to_oc.py` (Aufgabe in OCs Workspace legen), dann @OC in WhatsApp bitten
- **Workaround Logikketten:** `POST /api/oc/trigger_whatsapp_plan` – versucht API, bei 405 automatisch Fallback (Task in Workspace). Für HA-Logikschalter siehe Abschnitt „Workaround: Logikschalter in HA“.
