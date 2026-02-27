# Kontext für Dev-Agent: ATLAS-OC-Kanal prüfen und aufsetzen

Der Dev-Agent soll die Kommunikation zwischen ATLAS und OC (OpenClaw) prüfen und eine konkrete Checkliste liefern, damit Daten bei OC landen und beide Seiten sich abstimmen können.

**Bezeichnung:** OC = OpenClaw (nicht anders bezeichnen).

---

## Auftrag: Von außen draufschauen

**Der Dev-Agent soll den Kanal ATLAS ↔ OpenClaw von außen analysieren und klar benennen, wo das Problem liegt.**

- Auf der **OpenClaw-Seite** ist der Kanal konfiguriert: OPENCLAW_GATEWAY_TOKEN gesetzt, Port (z. B. ATLAS_COM=18789) gesetzt – Umgebung läuft.
- Auf der **ATLAS-Seite** liefert `/api/oc/status` aktuell: **Timeout – Gateway nicht erreichbar**. Die Schnittstelle ist im Backend angeboten, aber das Gateway auf dem VPS antwortet von hier aus nicht.
- **Frage an den Dev-Agent:** Wo genau siehst du das Problem? (Mögliche Ebenen: .env auf ATLAS-Seite – VPS_HOST, OPENCLAW_GATEWAY_PORT; Firewall auf dem VPS – Port 18789 von außen offen?; OpenClaw-Gateway bindet nur auf localhost statt 0.0.0.0?; Netzwerk zwischen Marc-Rechner und VPS.) Konkrete Prüfpunkte und Reihenfolge nennen, damit der Kanal tatsächlich steht und ATLAS sich mit OpenClaw austauschen kann.

---

## Ausgangslage

- **Schnittstelle angeboten im Backend:** Unter `/api/oc/` (GET/POST). Siehe KANAL_ATLAS_OC.md. Status, Senden, Abholen (fetch) laufen über die laufende API – kein manuelles Skript nötig.
- **ATLAS → OC:** Nachrichten per HTTP POST an OpenClaw Gateway (`/v1/responses`). Code: `src/network/openclaw_client.py`; Backend: `POST /api/oc/send`.
- **OC → ATLAS:** OC legt JSON in `workspace/rat_submissions/` ab. ATLAS holt sie per `GET/POST /api/oc/fetch` (oder Skript `fetch_oc_submissions.py`) → `data/rat_submissions/`.
- **Problem:** OC hat bisher nichts erhalten (Timeout oder 405 beim Senden). Stammdokumente liegen nur im Repo, nicht auf dem VPS (Deploy nach Rat-Freigabe).

## Relevante Dokumente und Code

- [KANAL_ATLAS_OC.md](KANAL_ATLAS_OC.md) – Übersicht Kanal, Gateway-Config, Hinweis 405/Neustart
- [STAMMDOKUMENTE_DEPLOY.md](STAMMDOKUMENTE_DEPLOY.md) – Ablage Stammdokumente auf VPS, WhatsApp-Info an OC
- [UMSETZUNGSPLANUNG.md](UMSETZUNGSPLANUNG.md) – Task „Stammdokumente und Kanal zu OC“
- `src/network/openclaw_client.py` – gateway_url, auth_headers, send_message_to_agent
- `src/scripts/setup_vps_hostinger.py` – setzt `gateway.http.endpoints.responses.enabled: true` in openclaw_config
- `src/scripts/restart_openclaw_vps.py` – SSH zum VPS, `docker restart openclaw-gateway` (damit Config greift)
- `src/scripts/test_atlas_oc_channel.py` – Test Gateway + optional Senden
- `src/scripts/send_offene_punkte_to_oc.py` – Sendet Kontext + offene Punkte
- `src/scripts/deploy_stammdokumente_vps.py` – Kopiert Stammdokumente nach VPS
- `src/scripts/fetch_oc_submissions.py` – Liest rat_submissions vom VPS

## Erwartete Ausgabe des Dev-Agenten

1. **Checkliste „Daten bei OC ankommen“:** Konkrete Schritte in Reihenfolge (z. B. 1. Auf VPS openclaw.json prüfen/ergänzen, 2. Container neustarten, 3. test_atlas_oc_channel --send, 4. send_offene_punkte_to_oc ausführen, 5. Mit OC abstimmen).
2. **Hinweise zu typischen Fehlern:** 405, Timeout, „Nicht konfiguriert“ – was jeweils zu tun ist.
3. **Optional:** Kurze Empfehlung, ob zuerst Kanal (Nachricht senden) oder zuerst Stammdokumente auf Server deployen – und wie OC danach informiert wird.

Die Ausgabe wird in docs/DEV_AGENT_OC_KANAL_CHECKLISTE.md geschrieben. Der Cursor-Agent führt aus, was ohne Marc geht; nur VPS-Config/Neustart (und ggf. Rat) bleiben für Marc.

## Offene Punkte / Nächste Schritte (wieder aufnehmen)

1. **Nach (komplettem) Neustart:** Wenn OpenClaw/VPS neu gestartet wurde: ca. 10–30 s warten, dann `python -m src.scripts.test_atlas_oc_channel --send` und `python -m src.scripts.send_offene_punkte_to_oc` – prüfen, ob Daten bei OC ankommen. Bei Timeout: siehe KANAL_ATLAS_OC.md (Timeout – Gateway nicht erreichbar).
2. **Backend mit aktuellen Routen:** Sicherstellen, dass die laufende API die Routen aus `dev_agent_ws` geladen hat (z. B. Backend neu starten oder START_DEV_AGENT.bat), damit `/api/chat/history` und Restart nicht 404 geben und das Frontend „Backend verbunden“ anzeigt.
3. **Stammdokumente auf VPS (optional):** Nach Rat-Freigabe `python -m src.scripts.deploy_stammdokumente_vps` ausführen und OC per WhatsApp informieren (Vorlage in STAMMDOKUMENTE_DEPLOY.md).