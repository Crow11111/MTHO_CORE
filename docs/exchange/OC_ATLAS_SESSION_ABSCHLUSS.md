# OC ↔ ATLAS Session-Abschluss (für Marc morgen)

## Erledigt heute

1. **Stammdokumente + Briefing auf VPS:**  
   `deploy_stammdokumente_vps` ausgeführt. Abgelegt unter `/var/lib/openclaw/workspace/stammdokumente/`:
   - 00_INDEX.md, 01_PROJEKT_ATLAS.md, 02_MARC_UND_TEAM.md, 03_OC_ROLLE_UND_GRENZEN.md  
   - **OC_ABSTIMMUNG_UND_GRUSS.md** (OC-Punkte, Regeln, Gruss von Marc, „sorry dass es so lange gedauert hat“).  
   OC kann die Dateien im Workspace lesen.

2. **Backup:** Erstes Backup gestartet (daily_backup, Key-Auth). Archiv wird auf VPS nach `/var/backups/atlas` hochgeladen (lief beim Abschluss noch).

3. **SSH-Key:** Key „ATLAS“ bei Hostinger hinterlegt. Alle VPS-Skripte nutzen `VPS_SSH_KEY` (ohne Passwort).

4. **Kanal POST an OC:** Weiterhin **405** (Hostinger-Container akzeptiert POST /v1/responses nicht). Gruss/Kontext konnten **nicht live** an OC gesendet werden – liegen aber in `OC_ABSTIMMUNG_UND_GRUSS.md` im Workspace, OC hat Zugriff.

## Offen / morgen

- **Kanal 405:** Entweder Hostinger-Image anpassen/ersetzen oder dauerhaft unser Container (setup_vps_hostinger, Port 18789) nutzen und Firewall/Port prüfen.
- **OC-Abstimmung:** OC soll Briefing verarbeiten und kommentieren. Wenn OC neue Vorschläge macht: Gewichtung nach Rat, virtuelle Abstimmung; hohe Zustimmung → umsetzen, sonst → offene Fragen für dich.
- **DB auf VPS:** Chroma/Container-Status bei Gelegenheit prüfen (war als Quick-Check geplant, technisch unterbrochen).

## Regeln für ATLAS ↔ OC (aus Marc-Direktive)

- Neue Vorschläge von OC: nach Rat-Persönlichkeiten gewichten, Punkt-für-Punkt abstimmen. Hohe Zustimmung → Umsetzung, sonst offene Fragen.
- Kanal ohne Marc: Abstimmung und Bau zwischen ATLAS und OC; gebündeltes Feedback an Marc bei Bedarf.
- Themen-Clustering/Split-Analyse von OC als Kernfeature priorisiert; ATLAS aktiv synchron halten (alle Einträge scannen, kein Echochamber).

---

*Gute Nacht. OC hat die Dateipakete im Workspace.*
