# Stammdokumente für OC – Ablage auf Hostinger und Information

## Ablauf

1. **Stammdokumente** liegen im Repo unter [docs/stammdokumente_oc/](stammdokumente_oc/00_INDEX.md) (00_INDEX, 01_PROJEKT_ATLAS, 02_MARC_UND_TEAM, 03_OC_ROLLE_UND_GRENZEN).
2. **Freigabe durch den Rat:** Der Rat (Osmium Council) prüft die Stammdokumente. Wenn alle eine Stimme abgegeben haben und die Mehrheit dafür ist, gilt die Freigabe.
3. **Deployment:** Die Stammdokumente werden auf dem Hostinger-VPS an einer Stelle abgelegt, die **OC einsehen kann** (z. B. `/var/lib/openclaw/workspace/stammdokumente/`).
4. **Information:** Marc informiert **per WhatsApp** (über den OC-Kanal oder den HA-Pfad, je nachdem wo OC erreicht wird), dass die Stammdokumente dort liegen und einsehbar sind.
5. **Laufender Austausch:** Nach dem initialen Deploy findet die Abstimmung (Handshakes, Briefings, Feedback) ausschließlich über das Verzeichnis `docs/exchange/` statt.

## Skript: Stammdokumente auf VPS deployen

**Skript:** `src/scripts/deploy_stammdokumente_vps.py`

**Aufruf (aus Projekt-Root):**
```bash
python -m src.scripts.deploy_stammdokumente_vps
```

- Liest alle Dateien aus `docs/stammdokumente_oc/` (`.md`).
- Verbindet per SSH mit dem VPS (VPS_HOST, VPS_USER, VPS_PASSWORD aus .env).
- Legt sie ab unter `/var/lib/openclaw/workspace/stammdokumente/` (Verzeichnis anlegen, Rechte 1000:1000).
- Nur ausführen **nach** Freigabe durch den Rat.

## WhatsApp-Nachricht (nach Freigabe)

**Vorlage für die Information an OC** (per WhatsApp senden, so dass OC es lesen kann):

```
[ATLAS] Die Stammdokumente für dich liegen bereit. Sie befinden sich auf dem Server im OC-Workspace unter stammdokumente/ (00_INDEX.md, PROJEKT_ATLAS, MARC_UND_TEAM, OC_ROLLE_UND_GRENZEN). Dort steht, was wir hier machen, warum, wer Marc ist, wer das Team ist und wie deine Rolle und Grenzen definiert sind.
```

(Der Präfix [ATLAS] kennzeichnet Nachrichten vom vollen ATLAS/Dreadnought; siehe WHATSAPP_E2E_HA_SETUP.md / DEV_AGENT_UND_SCHNITTSTELLEN – Abschnitt WhatsApp-Präfix.)

---

*Referenz: DOCS_INDEX.md, stammdokumente_oc/00_INDEX.md.*
