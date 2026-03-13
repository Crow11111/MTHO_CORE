<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Fritzbox Netzwerk-Konfiguration

**Stand:** 2026-03-02  
**Ausgelesen via:** `src/scripts/_fetch_fritzbox_info.py` (TR-064 API)

---

## Hardware

| Parameter | Wert |
|-----------|------|
| Modell | FRITZ!Box 7583 |
| Firmware | 8.20 |
| IP (LAN) | 192.168.178.1 |
| MAC | 74:42:7F:CC:70:62 |
| Hostname | MaFritzBox |

---

## WAN-Verbindung

| Parameter | Wert |
|-----------|------|
| Status | Online |
| Externe IPv4 | 87.79.192.110 |
| Externe IPv6 | 2001:4dd0:af17:822b:7642:7fff:fecc:705f |

---

## DHCP-Konfiguration

| Parameter | Wert |
|-----------|------|
| DHCP Server | Aktiviert |
| DHCP Range | 192.168.178.2 – 192.168.178.200 |
| Subnetzmaske | 255.255.255.0 |
| Standard-Gateway | 192.168.178.1 |
| DNS Server (für Clients) | **192.168.178.54** (Home Assistant / AdGuard) |
| Domain | MaFritzBox |
| DHCP Relay | Deaktiviert |

**Wichtig:** Die Fritzbox verteilt `192.168.178.54` als DNS – das ist Home Assistant mit AdGuard. Damit läuft der gesamte DNS-Traffic über AdGuard.

---

## Kritische Geräte (aktiv, mit fester IP)

| Name | IP | MAC | Funktion |
|------|----|----|----------|
| HOME | 192.168.178.54 | 2C:CF:67:68:45:32 | **Home Assistant / AdGuard DNS** |
| MtH11 | 192.168.178.20 | 18:C0:4D:DB:2D:B0 | Haupt-PC (4D_RESONATOR (CORE)) |
| HACS-PI4 | 192.168.178.154 | E4:5F:01:8C:22:46 | Raspberry Pi 4 |
| DCS-6100LH | 192.168.178.100 | B0:C5:54:5D:B3:61 | D-Link Kamera |
| samsungq95 | 192.168.178.123 | C0:23:8D:EB:07:1D | Samsung TV (LAN) |
| Mini-Regal | 192.168.178.108 | F0:EF:86:0D:A9:0E | Google Mini |
| Google-Nest-Mini | 192.168.178.23 | 20:1F:3B:78:08:64 | Google Mini (Flur) |
| MiniSTisch | 192.168.178.28 | E4:F0:42:1F:DB:EB | Google Mini (Schreibtisch) |
| minis1 | 192.168.178.4 | 14:C1:4E:94:CB:77 | Google Mini |
| Center | 192.168.178.80 | DC:E5:5B:6A:85:B2 | Sonos/Center |
| VMSucker | 192.168.178.91 | 78:11:DC:5F:F7:4D | Staubsauger |
| p1s3d | 192.168.178.95 | 24:58:7C:DF:3B:A0 | 3D-Drucker |

---

## ESP/Smart-Home Geräte (aktiv)

| Name | IP | MAC |
|------|----|----|
| ledcontrollernew | 192.168.178.15 | B4:E8:42:28:7C:3A |
| ledkueche | 192.168.178.17 | B4:E8:42:DF:42:66 |
| Flur | 192.168.178.22 | 10:D5:61:1A:21:D7 |
| ESP-EAEACC | 192.168.178.26 | DC:4F:22:EA:EA:CC |
| ESP-Bettlicht | 192.168.178.27 | 24:A1:60:19:71:98 |
| ESP-PIR-Keller | 192.168.178.29 | 80:7D:3A:48:2B:06 |
| ESP-Deckenlampe | 192.168.178.30 | 10:D5:61:2C:0D:79 |
| Schreibtischlicht | 192.168.178.33 | 98:17:3C:3B:F2:C4 |
| protuer | 192.168.178.34 | 60:74:F4:87:61:D8 |
| ProTisch | 192.168.178.35 | D4:AD:FC:AC:68:EA |
| proregal | 192.168.178.36 | 60:74:F4:84:1C:04 |
| Andon1 | 192.168.178.37 | D0:C9:07:6D:37:B2 |
| Andon2 | 192.168.178.38 | D0:C9:07:70:97:C6 |
| Temp-Bridge | 192.168.178.39 | D8:1F:12:F6:29:AA |
| espbad | 192.168.178.42 | 70:89:76:92:2B:D2 |
| C52A | 192.168.178.43 | BC:07:1D:B9:5F:22 |
| Mehrfachsteckdose | 192.168.178.87 | 50:8B:B9:AE:61:63 |

---

## Netzwerk-Infrastruktur

| Name | IP | MAC | Typ |
|------|----|----|-----|
| powerlinemain | - | 34:31:C4:D0:18:1E | Powerline-Adapter |
| fritz.powerline | 192.168.178.31 | 42:49:79:F1:76:CF | Fritz Powerline |
| wlan0 | 192.168.178.21 | A0:92:08:FF:22:EF | WLAN-Gerät |
| wlan0 | 192.168.178.117 | 70:89:76:93:5E:0E | WLAN-Gerät |
| pc-proregal | 192.168.178.32 | 60:74:F4:24:4C:EC | PC/Regal |

---

## Bekannte Einschränkungen

1. **IPv6 DNS:** Die Fritzbox 7583 gibt per DHCPv6 trotzdem sich selbst als DNS aus. Google Minis bevorzugen IPv6 und umgehen damit AdGuard. Siehe `ADGUARD_HOME_SETUP.md`.

2. **Hairpin-NAT:** Nicht aktiviert (Standard). Externe URLs (z.B. `mth-home2go.duckdns.org`) funktionieren intern nur, wenn AdGuard/DNS die Domain auf die lokale IP umschreibt.

3. **TR-064 Limitierung:** Erweiterte Einstellungen (Portfreigaben, MyFRITZ, etc.) sind über TR-064 nicht vollständig abrufbar.

---

## Zugriff

- **Web-UI:** http://192.168.178.1 oder http://fritz.box
- **API-User:** `HA_AC` (in `.env` als `FRITZBOX_USERNAME`)
- **Skript:** `src/scripts/_fetch_fritzbox_info.py`

---

## Referenzen

- `docs/03_INFRASTRUCTURE/ADGUARD_HOME_SETUP.md` – AdGuard DNS-Konfiguration
- `docs/03_INFRASTRUCTURE/FRITZBOX_ADGUARD_ZERTIFIKAT.md` – Troubleshooting bei Zertifikat-/IP-Problemen
