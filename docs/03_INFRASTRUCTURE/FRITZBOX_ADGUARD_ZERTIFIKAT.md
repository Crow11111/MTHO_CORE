<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Fritzbox, AdGuard, Zertifikate – Checkliste

**Kontext:** Wenn `fritz.box` nicht erreichbar ist oder Zertifikatsfehler (z. B. HA/Scout unter 192.168.178.54) auftreten, oft: AdGuard/DNS oder geänderte IPs.

---

## 1. Fritzbox-Oberfläche erreichen

- **Standard-IP:** http://192.168.178.1 (Werkseinstellung)
- **Reserve:** http://169.254.1.1
- **Hostname:** fritz.box (funktioniert nur, wenn DNS im LAN die Fritzbox auflöst)

Wenn die Meldung kommt „Sie sind nicht mit Ihrer FRITZ!Box im Heimnetz verbunden“:
- Prüfen: Bin ich im gleichen WLAN/LAN wie die Fritzbox?
- Wenn **AdGuard** (oder anderes DNS-Filter) läuft: Fritzbox und ggf. dein PC als **Clients freigeben** bzw. DNS für fritz.box/192.168.178.1 nicht blockieren/umleiten. Beim ersten AdGuard-Setup mussten dafür oft alle Clients eingetragen werden.

---

## 2. IP-Wechsel prüfen (wegen Zertifikat)

Wenn sich eine **Geräte-IP** geändert hat (z. B. Scout, HA, 4D_RESONATOR (CORE)), passt das Zertifikat oft nicht mehr (ausgestellt für alte IP).

- **In der Fritzbox:**  
  **Heimnetz → Netzwerk → Netzwerkverbindung** (oder **Heimnetz → Netzwerk → Geräte**): Liste der Geräte und zugewiesene IPv4-Adressen. Prüfen, ob z. B. Scout/HA noch 192.168.178.54 haben oder ob die IP gestern/heute gewechselt hat.
- **Statische Zuordnung (DHCP-Reservierung):** Damit sich die IP nicht ändert: In der Fritzbox für das Gerät (z. B. Scout) eine feste IP zuweisen („Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen“).

---

## 3. AdGuard: Clients / DNS für Fritzbox

- **Damit fritz.box und 192.168.178.1 funktionieren:** In AdGuard die Fritzbox (und ggf. deinen Rechner) so einstellen, dass sie nicht blockiert/umgeleitet werden – z. B. „Clients“ bzw. „Geräte“ eintragen und von Filterung ausnehmen oder lokale Auflösung (fritz.box → 192.168.178.1) erlauben.
- **Lokale Domains:** Sicherstellen, dass lokale Namen (fritz.box, ggf. hostname von Scout/HA) von AdGuard korrekt durchgereicht werden (kein Block, keine falsche Weiterleitung).

---

## 4. Zertifikat nach IP-Wechsel (z. B. HA, Scout)

Wenn die **IP** eines Dienstes (HA, Scout) sich geändert hat:
- **Option A:** In der Fritzbox dem Gerät wieder die **alte IP** zuweisen (DHCP-Reservierung auf die bisherige IP).
- **Option B:** Zertifikat/HTTPS des Dienstes (HA, Scout) auf die **neue IP** ausstellen bzw. in HA/Scout so konfigurieren, dass die genutzte URL (IP oder Hostname) zum Zertifikat passt. Dann in CORE (z. B. `.env`: `HASS_URL`, Aufrufe zu HA) die richtige URL nutzen.

---

**Stand:** 2026-03. Bei erneutem Auftreten: zuerst Fritzbox-IP-Liste prüfen, dann AdGuard-Clients/DNS, dann Zertifikat/URL in CORE.
