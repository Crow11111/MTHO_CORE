# VPS IP-Monitoring und Automatisierung

**Stand:** 2026-03-04

---

## Problem: Dynamische VPS-IP bei Hostinger

Hostinger VPS (KVM) haben **keine garantiert statische IP**. Die IP kann sich ändern bei:

1. **VPS-Neustart** (selten, aber möglich)
2. **Hostinger-Wartung** (Datacenter-Migration)
3. **Manueller Neustart via Panel**

**Beobachtung 2026-03-02 → 2026-03-04:**
- IP war `187.77.68.250`
- Danach Timeout bei SSH → IP hat sich geändert

---

## Auswirkungen

| Betroffenes System | Symptom |
|---|---|
| `.env` (`VPS_HOST`, `OPENCLAW_ADMIN_VPS_HOST`) | SSH-Verbindung schlägt fehl |
| ChromaDB-Sync | Tunnel kann nicht aufgebaut werden |
| OpenClaw Gateway | API nicht erreichbar |
| Dokumentation | Veraltete IP-Referenzen |

---

## Lösung: Automatisches IP-Monitoring

### Option A: Hostinger API (empfohlen)

Hostinger bietet eine API zum Abrufen der aktuellen VPS-IP:

```bash
# API-Key im Hostinger Panel unter "API-Zugang" generieren
curl -H "Authorization: Bearer $HOSTINGER_API_KEY" \
  https://api.hostinger.com/v1/vps/{server_id}
```

**TODO:** Hostinger API-Key generieren und in `.env` als `HOSTINGER_API_KEY` hinterlegen.

### Option B: DuckDNS für VPS (einfach)

VPS registriert seine IP automatisch bei DuckDNS:

```bash
# Auf VPS als Cron-Job (alle 5 Min):
*/5 * * * * curl -s "https://www.duckdns.org/update?domains=atlas-vps&token=$DUCKDNS_TOKEN&ip="
```

Dann in `.env`:
```
VPS_HOST="atlas-vps.duckdns.org"
```

**Vorteil:** IP-Änderung wird automatisch propagiert, keine manuelle Anpassung nötig.

### Option C: Manuell (aktueller Stand)

1. Im Hostinger Panel einloggen
2. VPS → Übersicht → IP-Adresse kopieren
3. `.env` aktualisieren (`VPS_HOST`, `OPENCLAW_ADMIN_VPS_HOST`)
4. Dokumentation mit neuer IP aktualisieren

---

## Skript: IP-Check und .env-Update

```python
# src/scripts/check_vps_ip.py
# TODO: Implementieren wenn Hostinger API-Key vorhanden
```

---

## Empfehlung

**Kurzfristig:** Option C (manuell) – aktuelle IP im Hostinger Panel prüfen und `.env` aktualisieren.

**Mittelfristig:** Option B (DuckDNS) – einmalig auf VPS einrichten, dann automatisch.

**Langfristig:** Option A (Hostinger API) – vollautomatisch mit Health-Monitoring.

---

## Daten-Sicherheit bei IP-Wechsel

Die Daten auf dem VPS bleiben **erhalten**. Der IP-Wechsel betrifft nur die Netzwerk-Adresse, nicht den Storage. Docker-Volumes (`chroma_data`, etc.) sind persistent.

**Prüfung nach IP-Wechsel:**
1. SSH auf VPS mit neuer IP
2. `docker ps` – Container sollten noch laufen
3. `docker volume ls` – Volumes intakt
4. ChromaDB-Sync ausführen zur Bestätigung

---

## Referenzen

- `docs/04_PROCESSES/STANDARD_AKTIONEN_UND_NACHSCHLAG.md`
- `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md`
