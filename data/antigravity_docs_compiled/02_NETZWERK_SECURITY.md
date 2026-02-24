# 02 NETZWERK SECURITY

## Sektion 1

**Sektion 1: VLAN Topologie und mTLS-Zertifikats-Kette**

**1.1 Einleitung**

Die beiden Unternehmen, Alpha und Beta, planen eine vertrauenswürdige Verbindung über das Internet aufzubauen. Hierfür wird die Verwendung von VLAN (Virtual Local Area Network) mit 802.1Q-Schicht 2-Tagging und mTLS (mutual Transport Layer Security) Zertifikats-Kette mit einer internen CA (Certificate Authority) implementiert.

**1.2 Topologie**

Die Netzwerktopologie besteht aus zwei Standorten, Alpha und Beta. Jeder Standort verfügt über einen eigenen Core-Switch, der als VLAN-Router fungiert. Die beiden Standorte sind über das Internet miteinander verbunden.
```
 +-----------+          +-----------+
|  Core-Switch (Alpha)   |  Core-Switch (Beta)   |
|  (VLAN-Router)        |  (VLAN-Router)        |
+-----------+          +-----------+
       |                       |
       |  Internet              |
       |                       |
       v                       v
+-----------+          +-----------+
|  Server Alpha    |  Server Beta     |
|  (mTLS-Client)   |  (mTLS-Server)    |
+-----------+          +-----------+
```
**1.3 VLAN-Konfiguration**

Die folgende Tabelle zeigt die VLAN-Konfiguration für jeden Standort:
| VLAN-Id | Netzwerk-Adresse | Beschreibung |
| --- | --- | --- |
| 10 | 192.168.1.0/24 | Alpha-Intranet |
| 20 | 192.168.2.0/24 | Beta-Intranet |

**1.4 mTLS-Zertifikats-Kette**

Die mTLS-Zertifikats-Kette besteht aus drei Komponenten:

1. **Internale CA (Alpha)**: Eine eigene internale CA wird auf dem Server Alpha eingerichtet.
2. **Server-Zertifikat (Beta)**: Ein Zertifikat für den Server Beta wird von der internalen CA Alpha generiert und ausgegeben.
3. **Client-Zertifikat (Alpha)**: Ein Zertifikat für den Client Alpha wird von der internalen CA Alpha generiert und ausgegeben.

**1.5 Konfiguration**

Die folgenden Konfigurationsparameter werden benötigt:

* Internale CA Alpha:
 + Private Key: `RSA-2048`
 + Public Key: `SHA256-RSA`
 + Zertifikat-Algorithmus: `ECDSA-P384`
* Server-Zertifikat Beta:
 + Serialnummer: `1234567890abcdef`
 + Gültigkeitsdauer: `365 Tage`
* Client-Zertifikat Alpha:
 + Serialnummer: `fedcba0987654321`
 + Gültigkeitsdauer: `365 Tage`

**1.6 Mathematische Formeln**

Die Sicherheit der mTLS-Verbindung wird durch die Verwendung von Public-Key-Kryptographie sichergestellt. Die Sicherheitsstärke wird mathematisch wie folgt berechnet:

* Schlüssellänge (n): `2048`
* Sicherheitsstufe (s): `s = 128 - 3 \* log_2(n)`

Die Sicherheitsstufe `s` stellt die Anzahl der benötigten Bit zur Sicherung der Kommunikation dar.

---

## Sektion 2

**Sektion 2: Sicherheitsmaßnahmen**

### 2.1 Zero-Trust Policy

*   Einrichtung eines Zero-Trust-Zugriffsmodells, bei dem kein Computer oder Benutzer automatisch vertraut wird
*   Verwendung von Identity and Access Management (IAM) für die Authentifizierung und Autorisierung
*   Implementierung der Principle of Least Privilege (PoLP), um sicherzustellen, dass Benutzer nur den notwendigen Zugriff auf Ressourcen erhalten

#### 2.1.1 Einrichtung eines Zero-Trust-Zugriffsmodells

*   Verwendung von Active Directory Federation Services (ADFS) für die Authentifizierung und Autorisierung
*   Implementierung einer Identity Provider (IdP)-Architektur mit einem Identity Gateway (IG)
*   Konfiguration von Sicherheitsgruppen und -richtlinien für das dynamische Zuweisen von Zugriffsrechten

### 2.2 SSH-Tunneling mit ed25519-Schlüsseln

*   Einrichtung einer SSH-Infrastruktur mit öffentlichen Schlüsselverifizierung (ed25519)
*   Konfiguration von SSH-Tunneln für die sichere Übertragung sensibler Daten
*   Implementierung von SSH-Agenten und -Clients für die automatisierte Authentifizierung

#### 2.2.1 Einrichtung einer SSH-Infrastruktur mit öffentlichen Schlüsselverifizierung (ed25519)

```python
# Beispielkonfiguration für OpenSSH
Host *
    HostName example.com
    User username
    IdentityFile ~/.ssh/id_ed25519

# Beispielkonfiguration für Private Key
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABHcwgg...
-----END OPENSSH PRIVATE KEY-----
```

### 2.3 Port-Sperren auf Host-Ebene mittels Windows Firewall und IPTables

*   Einrichtung eines Windows-Firewalls mit definierten Sicherheitsregeln
*   Implementierung von IPTables-Richtlinien für die Steuerung des Netzwerkverkehrs

#### 2.3.1 Konfiguration eines Windows-Firewalls

```powershell
# Beispielkonfiguration für ein eingehendes Regelset:
New-NetFirewallRule -DisplayName "Eingehender SSH-Traffic" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22

# Beispielkonfiguration für ein ausgehendes Regelset:
New-NetFirewallRule -DisplayName "Ausgehender DNS-Traffic" -Direction Outbound -Action Allow -Protocol UDP -LocalPort 53
```

#### 2.3.2 Implementierung von IPTables-Richtlinien

```bash
# Beispielkonfiguration für ein eingehendes Regelset:
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Beispielkonfiguration für ein ausgehendes Regelset:
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
```

**Hinweis:** Diese Beispiele dienen nur zur Verdeutlichung und müssen je nach Umgebung angepasst werden.

---

