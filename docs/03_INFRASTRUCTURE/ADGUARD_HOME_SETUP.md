<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# AdGuard Home - DNS Server (Scout)

## Überblick
- Rolle: Zentraler DNS-Server für das LAN (Pi-hole-Ersatz)
- Läuft als HA-Addon auf Scout (192.168.178.54)
- Addon-Slug: `a0d7b954_adguard`, Version: v0.107.72
- Web UI: http://192.168.178.54:3000
- `leave_front_door_open` ist aktiv (kein Login für API)

## Installation (HA Addon)
1. HA Web UI → Einstellungen → Add-ons → Add-on Store
2. "AdGuard Home" suchen → Installieren
3. Konfiguration Tab:
   - SSL: an (fullchain.pem / privkey.pem)
   - Port 53 (DNS) auf Host exponiert
   - Port 3000 (Web UI) → 80/tcp
4. Starten

## DNS-Konfiguration
- Upstream DNS: `1.1.1.1`, `8.8.8.8`, `9.9.9.9`
- Bootstrap DNS: `1.1.1.1`, `8.8.8.8`
- Protection: aktiviert

## DNS-Rewrites
| Domain | Antwort | Zweck |
|--------|---------|-------|
| mth-home2go.duckdns.org | 192.168.178.54 | HA lokal auflösbar |
| api.govee.com | *.api.govee.com | Govee-Geräte |

## DHCP-Server
AdGuard DHCP ist aktiviert (parallel zur FritzBox):
- Interface: `end0`
- Range: 192.168.178.20 - 192.168.178.199
- Gateway: 192.168.178.1
- Statische Leases für alle Google/Nest-Geräte eingerichtet

**Wichtig:** FritzBox DHCP läuft parallel. Die FritzBox gibt per DHCPv6 immer sich selbst als DNS aus. Google Minis bevorzugen IPv6-DNS und umgehen damit AdGuard.

## FritzBox-Konfiguration
- Internet → Zugangsdaten → DNS-Server:
  - DNSv4: 192.168.178.54 (AdGuard), Fallback: 1.1.1.1
  - DNSv6: fd8d:4ce:b6e8:0:2a5a:f9e5:c0bd:455c (Scout ULA)
- Heimnetz → Netzwerk → IPv4: Lokaler DNS = 192.168.178.54
- Heimnetz → Netzwerk → IPv6: DNSv6-Server im Heimnetz = Scout ULA

**Bekannte Einschränkung:** Die FritzBox 7583 gibt per DHCPv6 trotzdem sich selbst als DNS aus. Google Minis fragen daher die FritzBox statt AdGuard. Siehe TTS-Fix unten.

## TTS auf Google Minis -- Die Lösung

**Problem:** Google Minis bekommen TTS-Audio-URLs von HA. Wenn die URL `https://mth-home2go.duckdns.org/...` enthält und die Minis die Domain auf die externe IP auflösen (weil sie den FritzBox-DNS nutzen), können sie das Audio nicht laden (SSL-Zertifikat passt nicht / Server nicht erreichbar).

**Lösung:** HA `external_url` auf die lokale IP setzen:
```
external_url: https://192.168.178.54:8123
internal_url: http://192.168.178.54:8123
```
HA erkennt, dass Cast-Geräte die lokale HTTPS-URL nicht mit gültigem Zertifikat laden können, und routet die TTS-Audio-URLs automatisch über **Nabu Casa Cloud** (`*.ui.nabu.casa`). Nabu Casa hat gültige öffentliche SSL-Zertifikate, die die Minis akzeptieren.

**Gesetzt via:** WebSocket API `config/core/update`

## Verifizierung
```bash
# AdGuard DNS-Rewrite prüfen
nslookup mth-home2go.duckdns.org 192.168.178.54
# Erwartetes Ergebnis: 192.168.178.54

# TTS-Test
# TTS-URLs sollten über nabu.casa geroutet werden:
# https://5fggbz3aeugcmhkxm9egldv4fw3dgplh.ui.nabu.casa/api/tts_proxy/...
```

## Blocklisten (Pi-hole-Ersatz)
- Standard-Blockliste von AdGuard (vorinstalliert)
- Optional: Steven Black Unified Hosts
- Optional: OISD Full

## Status
- [x] Addon installiert und gestartet
- [x] DNS-Upstream konfiguriert (1.1.1.1, 8.8.8.8, 9.9.9.9)
- [x] DNS-Rewrite für DuckDNS aktiv
- [x] FritzBox DNS umgestellt (v4 + v6)
- [x] DHCP mit statischen Leases für Google-Geräte
- [x] TTS funktioniert auf Google Minis (via Nabu Casa Routing)
- [x] Google TTS verifiziert (2026-03-01)
- [x] ElevenLabs TTS verifiziert (2026-03-01)
