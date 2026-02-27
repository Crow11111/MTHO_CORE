# WhatsApp: OC (OpenClaw) vs. HA-Pfad – Evaluierung

**OC = OpenClaw** (Kurzbezeichnung im Projekt). Kurze Gegenüberstellung und Einfluss auf unsere Umsetzung.

**Spätere Kanäle & letzte Instanz:** OC ist in WhatsApp aktiv. Später brauchen wir **getrennte Kanäle**, damit OC keinen Zugriff auf Chats hat, in denen Steuerbefehle laufen (OC könnte sonst Dinge außerhalb seiner Sandbox anstoßen). Lokales **ATLAS** behält die **letzte Entscheidungsgewalt**; Einfallstore regelmäßig prüfen. Details: UMSETZUNGSPLANUNG, DEV_AGENT_UND_SCHNITTSTELLEN.

---

## 1. OC (OpenClaw): nativ ein Kanal

**Wie es funktioniert:**
- Das **OC-Gateway** (OpenClaw, auf dem VPS) betreibt WhatsApp **direkt** über die **Baileys**-Bibliothek (WhatsApp-Web-Protokoll).
- Einmaliges **QR-Login** (`openclaw channels login`), danach hält das Gateway die Session (Socket, Inbox-Loop).
- **Eingehende Nachricht** → Gateway empfängt sie nativ → **Routing/Bindings** → Session/Queue → **Agent-Run** → Antwort wird **über denselben Kanal** zurückgeschickt (deterministisches Routing, keine zweite „Nummer“).
- Konfiguration: `channels.whatsapp` in `openclaw.json` (z. B. `dmPolicy`, `allowFrom`, `textChunkLimit`). Unser VPS-Setup setzt bereits `allowFrom` aus `WHATSAPP_TARGET_ID`.

**Eigenschaften:**
- **Ein System, eine Verbindung:** Das Gateway „besitzt“ die WhatsApp-Session; keine Vermittlung über HA oder einen anderen Dienst.
- **Antworten** gehen automatisch in denselben Chat (gleicher Absender/Thread).
- **Kein Webhook** im Sinne „externer Dienst ruft uns auf“ – der Kanal ist im Gateway integriert.

---

## 2. Unser HA-Pfad (ATLAS über gajosu-Addon)

**Wie es funktioniert:**
- **Dein** WhatsApp-Account ist mit dem **gajosu/whatsapp-ha-addon** in HA verbunden (ebenfalls WhatsApp-Web/Baileys-ähnlich, aber im Addon).
- **Eingehende Nachricht** in deinem Account → Addon löst ein **HA-Event** aus (z. B. `whatsapp_message_received`) mit Payload (Absender, Nachricht, ggf. Media).
- **HA-Automation** reagiert auf das Event und ruft **rest_command.atlas_whatsapp_webhook** auf – dieser macht einen **HTTP-POST** an ATLAS_CORE (`/webhook/whatsapp`) mit dem Event-Payload.
- **ATLAS** verarbeitet die Nachricht (Triage, LLM, Steuerung) und antwortet per **ha_client.send_whatsapp(to_number=sender, text=reply)** → HA-Service **whatsapp/send_message** → Addon schickt die Nachricht zurück in den Chat.

**Eigenschaften:**
- **Zwei Systeme:** HA (Addon) hält die WhatsApp-Verbindung; ATLAS (Dreadnought) ist ein Backend, das per Webhook aufgerufen wird und über HA-Dienste zurücksendet.
- **E2E-Kette:** Echte Nachricht → HA-Event → rest_command → ATLAS-Webhook → ATLAS antwortet über HA → Antwort im gleichen Chat.

---

## 3. Vergleich & Einfluss auf unsere Umsetzung

| Aspekt | OC (OpenClaw, nativ) | HA-Pfad (ATLAS) |
|--------|----------------------|------------------|
| **Wer hält WhatsApp?** | OC-Gateway (VPS) | HA-Addon (Scout) |
| **Wo läuft die „Intelligenz“?** | OC-Agents (auf dem Gateway / angebunden) | ATLAS_CORE (Dreadnought), aufgerufen per Webhook |
| **Antwortweg** | Gateway sendet direkt in den Kanal zurück | ATLAS ruft HA-Service `whatsapp/send_message` auf |
| **E2E-Test** | Nachricht an die am OpenClaw angemeldete Nummer senden → Antwort von OpenClaw prüfen | Nachricht in deinen Account (Addon) → Automation → rest_command → ATLAS → Antwort im Chat prüfen |

**Einfluss auf unsere Umsetzung:**
- **OC** ersetzt **nicht** den HA-Pfad: OC nutzt eine **eigene** WhatsApp-Session (eigenes Gateway, ggf. eigene Nummer/Account), während der HA-Pfad **deinen** Account und das Addon nutzt. Beide können parallel existieren (zwei getrennte Wege). Später: getrennte Kanäle, damit OC keinen Zugriff auf Steuerbefehle-Chats hat; ATLAS = letzte Instanz.
- **E2E von HA** bleibt **essenziell**, wenn ATLAS auf Nachrichten reagieren soll, die **über deinen Account** im Addon ankommen. Dafür müssen wir sicherstellen:
  1. **HA-Automation:** Event (z. B. `whatsapp_message_received`) → Aufruf von `rest_command.atlas_whatsapp_webhook` mit Event-Daten.
  2. **rest_command** in HA: muss so konfiguriert sein, dass er ATLAS_CORE unter der richtigen URL (Dreadnought oder Scout) mit dem Payload aufruft.
  3. **ATLAS-API** läuft und ist von HA aus erreichbar; ATLAS antwortet per `send_whatsapp` über den HA-Service.
- **OC** können wir zusätzlich nutzen (z. B. zweiter Kanal, andere Nummer/Session); die **Umsetzung des HA-E2E** ist davon unabhängig und bleibt die Basis für „Nachricht an dich → ATLAS antwortet“.

---

## 4. Wie erreichst du den OC-Kanal? (Kein eigener „Kontakt“)

OC nutzt **keine eigene WhatsApp-Business-Nummer** und erscheint **nicht** als separater Kontakt auf dem Handy. Stattdessen:

- **Einmaliges Pairing:** Auf dem VPS (oder wo das OC-Gateway läuft) musst du den **WhatsApp-Kanal anmelden**: z. B. `openclaw channels login` → QR-Code anzeigen → mit **deinem Handy** unter WhatsApp „Verbundene Geräte“ den QR-Code scannen. Damit ist **deine Nummer** (oder die des genutzten Accounts) mit OC verbunden – wie ein zweites „WhatsApp Web“.
- **Der Kanal = diese verknüpfte Nummer:** Alle Nachrichten, die **an diese Nummer** in WhatsApp ankommen (auf deinem Handy sichtbar), werden an OC durchgereicht. OC antwortet aus derselben Session – die Antwort erscheint im **gleichen Chat** wie die eingehende Nachricht.
- **So „erreichst“ du den Kanal:** Du schickst eine Nachricht **an die Nummer, die mit OC verknüpft ist**. Wenn du deine eigene Nummer verknüpft hast: z. B. von einem zweiten Gerät **eine Nachricht an dich selbst** schicken – dann geht sie in deinen Account (und an OC). Oder jemand, dessen Nummer in `allowFrom` steht, schickt dir eine Nachricht – dann geht sie an deinen Account und OC empfängt sie.
- **Warum du keinen „Kontakt OC“ siehst:** Es gibt keinen zusätzlichen Chat. Der Kanal ist dein **eigener** Account, nur dass das Gateway (OC) die Nachrichten mitliest und beantwortet. Du siehst weiterhin deine normalen Chats; die Nachrichten, die an deine Nummer gehen, werden zusätzlich an OC gesendet.

**Kurz:** Nummer mit OC per QR verknüpfen → Nachrichten **an diese Nummer** (z. B. von anderem Gerät an dich selbst) = Nachrichten an den OC-Kanal. Antworten kommen im selben Chat.

---

## 5. Routing @Atlas / @OC und Antwortformat

- **@Atlas** am Anfang → ATLAS/Scout antworten mit **[ATLAS]** bzw. **[Scout]**.
- **@OC** am Anfang → nur OC antwortet mit **[OC]** oder @OC; ATLAS (HA-Pfad) reagiert nicht.
- Nur der adressierte Adressat reagiert; bei @Atlas + @OC später in der Nachricht gilt der Teil für den anderen bzw. beide. Vollständige Regeln und OC-Prozedere: **docs/WHATSAPP_ROUTING_ATLAS_OC.md**.

---

## 6. Referenzen

- OpenClaw: [Channels WhatsApp](https://openclaw.im/docs/channels/whatsapp), [Messages](https://docs.openclaw.ai/concepts/messages).
- Unser Setup: `setup_vps_hostinger.py` (OC `channels.whatsapp.allowFrom`), `wire_whatsapp_ha.py` (HA-Automation), `whatsapp_webhook.py` (ATLAS-Empfang), `ha_client.send_whatsapp` (Antwortweg).
