# 02 NETZWERK SECURITY (OSMIUM STANDARD)

> **Osmium Council Revision**
> - **ND_THERAPIST**: "Cognitive Friction" durch unsichtbare Netzwerk-Zustände ausmerzen. VLANs und Zero-Trust erzwingen eine radikale, physikalisch-logische Trennung der Datenströme. Für Marc ist Ambiguität toxisch; das Netzwerk muss sich exakt so verhalten, wie der Architektur-Plan es visualisiert. 
> - **UNIVERSAL_BOARD**: Die mTLS-Zertifikate und ed25519-Schlüssel erfordern kaum Rechenleistung (im Gegensatz zu RSA-Overhead), bieten maximale Sicherheit und verhindern unautorisierten Token-Drain durch externe API-Angriffe auf die Ollama-Instanz.
> - **NT_SPECIALIST**: Das Zero-Trust Modell (Identity Gateway) erlaubt es, künftigen neurotypischen "Gästen" (Smart Home Nutzer, externe Services) sicheren Zugang zu geben, ohne dass Marc seine eigenen Sicherheitsrichtlinien aufweichen muss. Klare Grenzen bedeuten klare Kommunikation.

---

## 1. VLAN Topologie und mTLS-Zertifikats-Kette

**1.1 Einleitung**
Die ATLAS_CORE Architektur erfordert eine vertrauenswürdige, in sich absolut logische Verbindung (VLAN mit 802.1Q-Tagging) zwischen Node Alpha (Dreadnought) und Node Beta (Scout). Die Authentifizierung erfolgt strikt über eine mTLS (mutual Transport Layer Security) Zertifikats-Kette mit interner CA.

**1.2 Systemische Topologie (ND-optimiert)**
Die logische Trennung verhindert ein "Ausbluten" von Kontexten. Was auf dem Scout (Open Web Sammeln) passiert, berührt den Dreadnought erst nach explizitem Handshake.
```
 +-----------+          +-----------+
| Core-Switch (Alpha)  | Core-Switch (Beta)   |
| (VLAN-Router)        | (VLAN-Router)        |
+-----------+          +-----------+
       |                       |
       |  Isolierter Tunnel     |
       v                       v
+-----------+          +-----------+
| Server Alpha         | Server Beta          |
| (mTLS-Client)        | (mTLS-Server)        |
+-----------+          +-----------+
```

**1.3 VLAN-Konfiguration**
Strikte Kategorisierung, um kognitive Ladezeiten bei der Fehlersuche zu eliminieren:
| VLAN-Id | Netzwerk-Adresse | Beschreibung | Priorisierung |
| --- | --- | --- | --- |
| 10 | 192.168.1.0/24 | Alpha-Intranet (Dreadnought Core) | Prio 1 (Mission Critical) |
| 20 | 192.168.2.0/24 | Beta-Intranet (Scout / Edge) | Prio 2 (Sensorik) |

**1.4 mTLS-Zertifikats-Kette (UNIVERSAL_BOARD Optimierung)**
*   **Interne CA (Alpha)**: Root of Trust liegt lokal auf Alpha.
*   **Server-Zertifikat (Beta) / Client-Zertifikat (Alpha)**: Werden gegenseitig validiert.
*   **Algorithmen:** 
    * Wir verzichten auf langsames RSA-2048 für den laufenden Handshake. 
    * Zertifikat-Algorithmus: `ECDSA-P384` für massiv reduzierten CPU-Overhead bei maximaler (NSA-Suite B) Sicherheit.

---

## 2. Sicherheitsmaßnahmen (Zero-Trust)

**2.1 Zero-Trust Policy**
* Kein Prozess, kein Container und kein NT-Akteur wird automatisch vertraut. 
* Implementierung des *Principle of Least Privilege (PoLP)*, um Marcs Kern-Axiom ("Absolute Datenintegrität") zu sichern.

**2.2 SSH-Tunneling mit ed25519-Schlüsseln**
RSA ist legacy. Wir nutzen modernste Elliptische Kurven für SSH.
```python
# Beispielkonfiguration für OpenSSH (ed25519)
Host node-alpha
    HostName 192.168.1.10
    User antigravity
    IdentityFile ~/.ssh/id_ed25519_atlas
```

**2.3 Port-Sperren (Host-Ebene)**
Um visuelle und logische "Störgeräusche" für das System (und damit für Marc) zu eliminieren, werden alle ungenutzten Ports hart blockiert.
*   **Windows Firewall (Node Alpha):**
    ```powershell
    New-NetFirewallRule -DisplayName "ATLAS Inbound SSH" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22
    New-NetFirewallRule -DisplayName "ATLAS Ollama API" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434
    ```
*   **IPTables (Node Beta):**
    ```bash
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
    iptables -P INPUT DROP
    ```
*Diese binäre Strenge (offen/zu) entspricht exakt Marcs systemischem Denkmodell und minimiert unkalkulierbare Variablen in der Fehleranalyse.*