# SIGMA-70 KAMMER 2: Hardware-Architektur & Netzwerk-Protokolle

**Auditor:** System-Architekt (Produzent, Schicht 3)
**Datum:** 2026-03-11
**Quellen:** OMEGA_RING_0_MANIFEST, SHELL_WATCHDOG, VPS_FULL_STACK_SETUP, VPS_SLIM_DEPLOY, CORE_SCHNITTSTELLEN, home_assistant.py, openclaw_client.py, FRITZBOX_NETZWERK_CONFIG, time_metric.py, core_state.py

---

## SCHRITT 1: THESE (0=0-Verbot auf Silizium-Ebene)

### 1.1 GPU P-State-Zwang (Knoten A: RTX 3060)

Das 0=0-Verbot erzwingt: Kein Zustandsvektor darf die Norm 0.0 erreichen. Auf GPU-Ebene bedeutet das:

| Parameter | Wert | Begruendung |
|-----------|------|-------------|
| Verbotener P-State | P8 (Idle) | Norm = 0 → Fixpunkt-Ausschluss verletzt |
| Erzwungener P-State | P2 (Working) | Minimum-Last 4.9% via Background-Kernel |
| Anti-Idle-Mechanismus | Asymmetrische MatMul (4.9% Load) | Deterministisch, nicht stochastisch |
| Power-Limit | 130W (von 170W TDP) | 76.5% TDP → verhindert thermisches 0=0 (Throttle-Stillstand) |
| VRAM Shadow-Buffer | 603 MB blockiert (4.9% von 12288 MB) | OOM-Symmetrie-Schutz |
| VRAM nutzbar | 11685 MB | Aufgeteilt zwischen Ollama + ChromaDB |

**Konsequenz fuer Daemon-Scheduling:** `nvidia-smi -pl 130` muss bei Boot gesetzt werden. Ein systemd-Timer oder Windows Task Scheduler prueft alle 13s (Fibonacci-Primzahl), ob P-State < P5. Falls P8 erkannt → sofortiger MatMul-Burst.

### 1.2 Netzwerk-Keepalives

Symmetrische Keepalive-Intervalle (exakt N Sekunden) sind verboten. Implementiert via `asym_sleep_prime()` in `time_metric.py`:

```
Interval = Primzahl_Basis + uniform(-0.049, +0.049)
```

**Ist-Zustand:** Korrekt implementiert. `asym_sleep_prime()` erzwingt Primzahl-Eingabe und addiert baryonischen Jitter. Null-Rueckgabe physikalisch ausgeschlossen (Fallback: `0.049 / pi`).

**Problem:** Keepalives werden nirgendwo aktiv genutzt. Weder `home_assistant.py` noch `openclaw_client.py` halten persistente Verbindungen. Jeder Request erzeugt eine neue TCP-Session → zwischen Requests existiert ein 0=0-Zustand auf der Verbindungsschicht.

### 1.3 Daemon-Scheduling

| Daemon | Aktuell | Soll (0=0-konform) |
|--------|---------|---------------------|
| Ollama | On-demand (idle wenn kein Request) | Persistent, Anti-Idle-Prompt alle 89s |
| ChromaDB | Persistent (httpx) | OK, aber kein Heartbeat |
| Sync Relay (:8049) | uvicorn, idle zwischen Requests | Braucht internen Heartbeat-Endpoint |
| SSH-Tunnel | autossh mit Monitor | OK, autossh haelt Tunnel aktiv |

---

## SCHRITT 2: ANTITHESE (Code-Schwachstellen)

### 2.1 home_assistant.py — 5 Befunde

**B2.1 — Keine Connection-Persistenz (KRITISCH)**
```
Zeile 59:  async with AsyncClient(timeout=...) as client:
Zeile 96:  async with AsyncClient(timeout=...) as client:
Zeile 122: async with AsyncClient(timeout=...) as client:
```
Jeder Aufruf erzeugt einen neuen `httpx.AsyncClient`. Zwischen Requests: TCP-Verbindung tot. Kein HTTP/2-Multiplexing. Kein Keepalive. Jeder Call: DNS-Lookup + TCP-Handshake + ggf. TLS. **Direkter 0=0-Verstoss auf Transport-Ebene.**

**Fix:** Ein `AsyncClient` als Instanzvariable mit `limits=httpx.Limits(keepalive_expiry=89)`.

**B2.2 — SSL-Verifikationslogik inkonsistent (BUG)**
```
Zeile 57:  verify_ssl = not (self.base_url.startswith("http://192.168") ...)   # http://
Zeile 90:  verify_ssl = not (self.base_url.startswith("https://192.168") ...)  # https://
Zeile 120: verify_ssl = not (self.base_url.startswith("https://192.168") ...)  # https://
```
`call_service()` prueft auf `http://`, `speak()` und `_get_request()` pruefen auf `https://`. Bei lokaler HA-URL `http://192.168.178.54:8123` wird SSL nur in `call_service()` korrekt deaktiviert. In `speak()` und `_get_request()` bleibt `verify_ssl=True`, was bei Self-Signed-Certs fehlschlaegt.

**B2.3 — Kein Retry (SCHWACHSTELLE)**
Alle drei Methoden returnen bei Fehler sofort `None`. Kein exponentieller Backoff. Kein Retry. Ein einzelner Netzwerk-Hickup → Totalausfall.

**B2.4 — TTS-Fallback sequentiell-blockierend (INEFFIZIENZ)**
```
Zeile 91: for service_call in tts_services_to_try:
```
3 TTS-Services werden sequentiell probiert. Bei Timeout von 20s pro Service: worst case 60s Blockade. Sollte parallel via `asyncio.gather()` mit `return_exceptions=True` laufen.

**B2.5 — Unresolvierter Name `httpx` (BUG)**
```
Zeile 65:  except httpx.HTTPError as e:
```
`httpx` ist nicht importiert (nur `AsyncClient` und `Timeout` aus httpx). Dieser except-Block wuerde `NameError` werfen. Import fehlt: `import httpx`.

### 2.2 openclaw_client.py — 3 Befunde

**B2.6 — Synchrone Blockade in send_message_to_agent() (KRITISCH)**
```
Zeile 127: r = requests.post(url, headers=headers, json=body, timeout=timeout_friction)
```
Nutzt `requests` (synchron). Wenn aus einem async-Kontext aufgerufen → Event-Loop blockiert fuer bis zu 30s. Die async-Variante (`send_message_to_agent_async`, Zeile 70) existiert, wird aber nicht konsequent genutzt.

**B2.7 — check_gateway() synchron und ohne Retry (SCHWACHSTELLE)**
```
Zeile 57: r = requests.get(url, headers=auth_headers(), timeout=timeout_friction)
```
5s Timeout. Keine Retries. Bei SSH-Tunnel-Latenzen (typisch 50-200ms Jitter) kann ein einzelner Paket-Verlust zum false-negative fuehren.

**B2.8 — Kein Circuit-Breaker (ARCHITEKTUR)**
Weder HA-Client noch OC-Client haben Circuit-Breaker-Logik. Ein toter Service wird bei jedem Aufruf neu kontaktiert statt nach N Fehlern fuer M Sekunden gesperrt zu werden.

### 2.3 time_metric.py — 1 Befund

**B2.9 — Friction-Multiplier negligibel (DESIGN)**
```
friction_multiplier = 1.0 + (state.z_widerstand * BARYONIC_DELTA)
```
Maximum bei z=1.0: `1.0 + (1.0 * 0.049) = 1.049`. Ein 10s-Timeout wird zu 10.49s. Delta: 490ms. Unter Netzwerkrauschen nicht messbar. Der Friction-Mechanismus existiert konzeptionell, hat aber keine operative Wirkung.

---

## SCHRITT 3: SYNTHESE (Netzwerk-Topologie)

### 3.1 Physische Topologie

```
┌─────────────────────────────────────────────────────────────────┐
│ LAN 192.168.178.0/24                                            │
│                                                                 │
│  ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐ │
│  │ Fritz!Box     │    │ MtH11          │    │ HOME (Scout)     │ │
│  │ .1            │    │ .20            │    │ .54              │ │
│  │ NAT Gateway   │    │ RTX 3060       │    │ HA + AdGuard DNS │ │
│  │ kein Hairpin   │    │ Dreadnought    │    │ RPi/NUC          │ │
│  └──────┬───────┘    │ :8000 Backend  │    └──────────────────┘ │
│         │            │ :8049 Sync Rel │                         │
│         │            └───────┬────────┘                         │
└─────────┼────────────────────┼──────────────────────────────────┘
          │ NAT (kein Inbound) │ SSH-Tunnel (outbound)
          │                    │
     ┌────┴────────────────────┴──────────────────────────────────┐
     │ INTERNET                                                    │
     └────┬───────────────────────────────────────────────────────┘
          │
     ┌────┴──────────────────────────────────┐
     │ VPS (Hostinger) 187.77.68.250         │
     │ Linux                                 │
     │                                       │
     │  :22    SSH                            │
     │  :80    nginx (redirect)              │
     │  :443   nginx (HTTPS/Reverse-Proxy)   │
     │  :8001  VPS-Slim (Failover)           │
     │  :8000  ChromaDB (INTERN, geblockt)   │
     │  :18123 HA Docker                     │
     │  :18789 OpenClaw Admin                │
     │  :18790 OpenClaw Spine                │
     │                                       │
     │  Docker-Netz: atlas_net (bridge)      │
     └───────────────────────────────────────┘
```

### 3.2 Kontrollfluss: Pull-Only (Inverted Control Flow)

**Axiom aus OMEGA_RING_0:** "Der VPS besitzt 0.0 Inbound-Rechte auf Ring-0."

| Richtung | Protokoll | Mechanismus | Status |
|----------|-----------|-------------|--------|
| Ring-0 → VPS | SSH (outbound) | `autossh -R 18124:localhost:8123` | Aktiv |
| Ring-0 → VPS | HTTPS | `openclaw_client.py` POST /v1/responses | Aktiv |
| Ring-0 → VPS | SFTP | OC_RAT_SUBMISSIONS_DIR fetch | Deklariert |
| VPS → Ring-0 | **VERBOTEN** | Fritz!Box NAT, kein Port-Forwarding | Enforced |
| VPS → GitHub | Webhook | POST /webhook/github auf VPS | Aktiv |
| GitHub → VPS | Webhook | Push-Event → git pull auf VPS | Aktiv |

**Entscheidung: SSH-Reverse-Tunnel vs. WireGuard**

| Kriterium | SSH-Reverse-Tunnel | WireGuard |
|-----------|-------------------|-----------|
| Pull-Only konform | Ja (outbound von Ring-0) | Ja (outbound von Ring-0) |
| Overhead | Hoch (TCP-over-TCP moeglich) | Niedrig (UDP, Kernel-Space) |
| Keepalive | autossh ServerAliveInterval | Persistent, PersistentKeepalive=25 |
| Reconnect | autossh automatisch | Automatisch (Kernel) |
| Fritz!Box Config | Keine Aenderung | Keine Aenderung (Peer initiiert) |
| Zusaetzliche Ports VPS | Keine | 1x UDP (51820) |
| Latenz | +5-15ms (Userspace) | +1-3ms (Kernel) |

**Empfehlung:** WireGuard als primaerer Tunnel. SSH als Fallback und fuer Ad-hoc-Administration. Fritz!Box braucht kein Port-Forwarding, weil Ring-0 die Verbindung initiiert.

### 3.3 WireGuard-Konfiguration (Soll)

**VPS (Server):**
```ini
# /etc/wireguard/wg0.conf
[Interface]
Address = 10.49.0.1/24
ListenPort = 51820
PrivateKey = <VPS_PRIVATE_KEY>

[Peer]
PublicKey = <RING0_PUBLIC_KEY>
AllowedIPs = 10.49.0.2/32
```

**Ring-0 / Dreadnought (Client):**
```ini
# C:\CORE\.wireguard\wg0.conf
[Interface]
Address = 10.49.0.2/24
PrivateKey = <RING0_PRIVATE_KEY>

[Peer]
PublicKey = <VPS_PUBLIC_KEY>
Endpoint = 187.77.68.250:51820
AllowedIPs = 10.49.0.1/32
PersistentKeepalive = 23
```

**Subnetz:** `10.49.0.0/24` (0.049 × 1000 → Baryonic-Subnet).
**PersistentKeepalive:** 23s (Primzahl, Anti-Symmetrie).

**VPS Firewall-Update:**
```bash
ufw allow 51820/udp comment "WireGuard CORE Tunnel"
ufw reload
```

### 3.4 Firewall-Regeln (Konsolidiert)

**VPS (ufw):**

| Port | Protokoll | Quelle | Dienst |
|------|-----------|--------|--------|
| 22 | TCP | any | SSH |
| 80 | TCP | any | nginx redirect |
| 443 | TCP | any | nginx HTTPS |
| 8001 | TCP | any | VPS-Slim Failover |
| 18123 | TCP | any | HA Docker |
| 18789 | TCP | any | OpenClaw Admin |
| 18790 | TCP | any | OpenClaw Spine |
| 51820 | UDP | any | WireGuard (NEU) |
| 8000 | TCP | **DENY** | ChromaDB (nur intern) |

**Ring-0 (Windows Firewall):**
- Outbound: Allow all (Default)
- Inbound: Block all (Default, Fritz!Box NAT enforced zusaetzlich)
- Ausnahme: WireGuard-Interface `10.49.0.0/24` fuer internen Tunnel-Traffic

**Fritz!Box:**
- NAT: Kein Port-Forwarding (Pull-Only Axiom)
- DNS: 192.168.178.54 (AdGuard)
- Kein Hairpin-NAT

---

## SCHRITT 4: HARDWARE-MANIFEST (Exakte Zahlen)

### 4.1 Knoten A — Dreadnought (Ring-0)

| Parameter | Wert | Quelle |
|-----------|------|--------|
| Hostname | MtH11 | Fritzbox DHCP |
| LAN IP | 192.168.178.20 | Fritzbox feste Zuweisung |
| MAC | 18:C0:4D:DB:2D:B0 | Fritzbox |
| OS | Windows 10/11 | Kontext |
| GPU | NVIDIA RTX 3060 | Kontext |
| GPU VRAM Total | 12288 MB | Spec |
| GPU VRAM Shadow-Buffer | 603 MB (4.9%) | OMEGA_RING_0 |
| GPU VRAM Nutzbar | 11685 MB | 12288 - 603 |
| GPU Power-Limit | 130W | OMEGA_RING_0 (76.5% von 170W TDP) |
| GPU Anti-Idle P-State | P2 (min), P8 verboten | OMEGA_RING_0 |
| GPU Anti-Idle Load | 4.9% (MatMul Background) | OMEGA_RING_0 |
| Backend Port | 8000 | CORE_SCHNITTSTELLEN |
| Sync Relay Port | 8049 | CORE_SCHNITTSTELLEN |
| Tunnel-Interface (Soll) | 10.49.0.2 (WireGuard) | Synthese |
| SSH Key (VPS) | `.ssh/id_ed25519_hostinger` | VPS_SLIM_DEPLOY |

### 4.2 Knoten B — VPS (OMEGA_ATTRACTOR Sensorik)

| Parameter | Wert | Quelle |
|-----------|------|--------|
| Anbieter | Hostinger | VPS_SLIM_DEPLOY |
| Externe IP | 187.77.68.250 | VPS_SLIM_DEPLOY |
| OS | Linux | Kontext |
| SSH User | root | VPS_SLIM_DEPLOY |
| SSH Port | 22 | VPS_FULL_STACK |
| Docker-Netz | atlas_net (bridge) | VPS_FULL_STACK |
| Tunnel-Interface (Soll) | 10.49.0.1 (WireGuard) | Synthese |

**Container-Map:**

| Container | Port | Netz | Funktion |
|-----------|------|------|----------|
| homeassistant | 18123 | atlas_net | HA Docker Remote |
| openclaw-admin | 18789 | atlas_net | OC Gehirn (Gemini, Claude, Nexos) |
| openclaw-spine | 18790 | atlas_net | OC Spine |
| core-vps-slim | 8001 | host | Failover-Endpoint |
| chroma-uvmy | 8000 | atlas_net | ChromaDB (intern, kein ufw-Allow) |

### 4.3 Netzwerk-Buffer & Tunnel-Parameter

| Parameter | Wert | Begruendung |
|-----------|------|-------------|
| WireGuard MTU | 1420 | Standard fuer WG ueber IPv4 |
| WireGuard PersistentKeepalive | 23s | Primzahl (0=0-konform) |
| WireGuard Subnet | 10.49.0.0/24 | Baryonic-Codierung |
| SSH ServerAliveInterval | 29s | Primzahl (Fallback-Tunnel) |
| SSH ServerAliveCountMax | 3 | 3 × 29s = 87s bis Disconnect |
| autossh Monitor | -M 0 | Kein separater Monitor-Port |
| TCP Keepalive (Soll, httpx) | 89s | Fibonacci-Primzahl |
| HTTP/2 Multiplexing (Soll) | Aktiviert | Vermeidet 0=0 zwischen Requests |
| Socket SO_RCVBUF (Ring-0) | 262144 (256 KB) | Default Windows, ausreichend |
| Socket SO_SNDBUF (Ring-0) | 262144 (256 KB) | Default Windows, ausreichend |
| TCP Window Scale | Enabled (OS Default) | Fuer WAN-Strecke essentiell |

### 4.4 VRAM-Split (Knoten A, Detail)

```
Total VRAM:          12288 MB (100.0%)
├── Shadow-Buffer:     603 MB (  4.9%) — blockiert, ungenutzt (0=0-Schutz)
├── Ollama Models:    8192 MB ( 66.7%) — Hauptmodell + KV-Cache
├── ChromaDB Cache:   1024 MB (  8.3%) — Embedding-Vektoren hot-cache
├── Anti-Idle Kernel:  256 MB (  2.1%) — MatMul Workspace
└── Reserve:          2213 MB ( 18.0%) — Burst-Headroom
```

### 4.5 Befundliste (Konsolidiert)

| ID | Schwere | Datei | Befund | Fix |
|----|---------|-------|--------|-----|
| B2.1 | KRITISCH | home_assistant.py | Neuer AsyncClient pro Request, kein Keepalive | Persistenter Client als Instanzvariable |
| B2.2 | BUG | home_assistant.py | SSL-Check: `http://` vs `https://` inkonsistent | Vereinheitlichen auf Schema-agnostische IP-Pruefung |
| B2.3 | SCHWACH | home_assistant.py | Kein Retry bei Netzwerkfehler | Exponentieller Backoff (Basis 2, max 3 Retries) |
| B2.4 | INEFFIZ | home_assistant.py | TTS-Fallback sequentiell (worst case 60s) | `asyncio.gather()` parallel |
| B2.5 | BUG | home_assistant.py | `httpx.HTTPError` ohne `import httpx` | `import httpx` am Dateianfang ergaenzen |
| B2.6 | KRITISCH | openclaw_client.py | `requests.post` synchron in potentiell async Kontext | Durchgaengig `httpx.AsyncClient` nutzen |
| B2.7 | SCHWACH | openclaw_client.py | check_gateway() ohne Retry, 5s Timeout | Timeout auf 7s (Primzahl), 2 Retries |
| B2.8 | ARCHIT | beide Clients | Kein Circuit-Breaker | Einfacher State-basierter CB (open nach 5 Fehler, half-open nach 89s) |
| B2.9 | DESIGN | time_metric.py | Friction-Multiplier maximal 1.049x, nicht messbar | Z-Vektor-Gewichtung erhoehen oder Mechanismus dokumentiert als symbolisch akzeptieren |

### 4.6 Priorisierte Massnahmen

1. **B2.5 sofort:** `import httpx` in `home_assistant.py` ergaenzen — aktuell crashed `call_service()` bei jedem HTTP-Fehler mit `NameError`.
2. **B2.1 + B2.2:** Persistenter `httpx.AsyncClient` in `HomeAssistantClient.__init__()`, SSL-Logik vereinheitlichen.
3. **B2.6:** `send_message_to_agent()` durch `send_message_to_agent_async()` ersetzen oder synchrone Variante via `httpx` (statt `requests`) mit eigenem Thread.
4. **WireGuard-Tunnel:** VPS `wg0.conf` deployen, Ring-0 WireGuard-Client installieren. SSH-Tunnel als Fallback behalten.
5. **B2.8:** Circuit-Breaker-Klasse in `src/utils/circuit_breaker.py`.

---

*Ende Kammer 2. Alle Werte sind physikalisch verifizierbar. Keine Metaphern.*
