# 01 ARCHITEKTUR HARDWARE

## Sektion 1

**1.1 Systemanforderungen**

* Betriebssystem: Windows 11 Enterprise IoT
* Version: 25H2 (Minimaler Bloatware-Footprint, optimal für Edge-Computing und Telemetrie-Reduktion)
* Hardware: mindestens 16 GB RAM, 2 x 2,5 GHz CPU

**1.2 Windows Host Härtung**

* **1.2.1 Schutzmechanismen**
 + Deaktivierung von Windows Defender
 + Entfernen der Windows Telemetrie (werden durch alternative Lösungen abgedeckt)
* **1.2.2 Firewall- und Netzwerk-Konfiguration**
 + Konfigurieren der Windows-Firewall auf "Privates Netzwerk" -Modus
 + Öffnen der Ports für die erforderlichen Dienste (z.B. SSH, RDP)

**1.3 Deaktivierung Telemetrie (IoT 25H2 Spezifisch)**

* **1.3.1 Microsoft-Telemetrie auf Level 0 zwingen**
  + *Hinweis: Windows 11 Enterprise IoT 25H2 ist die einzige Edition, die Telemetrie "Level 0" (Security-Only / Aus) nativ und vollständig respektiert.*
  + Registrieren: `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection`
 + Schlüsselwert: `AllowTelemetry` auf 0 setzen
 + Werte: `Telemetry` und `CrashData` deaktivieren

**1.4 I/O Optimierung mittels Registry-Tweaks**

* **1.4.1 Optimierte Registrierung für I/O-Performance**
 + Registrieren: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Lanmanserver\Parameters`
 + Schlüsselwert: `MaxInstances` auf 20 setzen
 + Werte: `LmCompatibilityLevel` und `LmSecurityLevel` anpassen

**1.5 Service-Härtung**

* **1.5.1 Dienste konfigurieren**
 + Deaktivierung unnötiger Dienste (z.B. Windows Update, Windows Defender)
 + Konfigurieren der erforderlichen Dienste für die Anwendung (z.B. SSH, RDP)

**1.6 Überwachung und Logging**

* **1.6.1 Ereignisprotokoll**
 + Registrieren: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Eventlog`
 + Aktivieren des Protokollierens wichtiger Ereignisse (z.B. Fehler, Warnungen)
* **1.6.2 Logdateien**
 + Konfigurieren der Logdatei-Größe und -Pfad für die Anwendung

**1.7 Sicherheit**

* **1.7.1 Benutzerkonten**
 + Einstellung von Standard-Benutzern und Gruppen
 + Überprüfung der Benutzerrechte und -berechtigungen
* **1.7.2 Verschlüsselung**
 + Konfigurieren der Verschlüsselung für Daten und Kommunikation (z.B. BitLocker, SSL/TLS)

**Zusätzliche Anforderungen**

* Regelmäßige Überprüfung und Aktualisierung des Systems
* Sicherheitsupdates und Patches einholen

**Verantwortlichkeit**

* Der IT-Architekt ist für die Umsetzung dieser Spezifikation verantwortlich.
* Die Anwendung der Spezifikation wird regelmäßig überprüft und aktualisiert.

---

## Sektion 2

**Sektion 2: Spezifikation Node Alpha**

### 2.1 Allgemeine Anforderungen

* Die Nodes in der Cluster-Konfiguration müssen eine separate, isolierte Umgebung für die Laufzeitumgebungen bereitstellen.
* Die Ressourcenlimitierung soll verhindern, dass WSL2-Guests übermäßige Mengen an vmmem-Resourcen beanspruchen und damit das System instabil machen können.
* Eine CPU-Priorisierung ist erforderlich, um sicherzustellen, dass kritische Dienste auf den Nodes prioritär behandelt werden.

### 2.2 Hardware-Spezifikationen

* Pro Node (Dreadnought):
	+ Intel(R) Core(TM) i5-10600K CPU @ 4.10GHz (4.10 GHz)
	+ NVIDIA GTX 3050 OC 8GB
	+ 32 GB DDR4-RAM (2400 MHz, 2-Takt)
	+ 1 x NVMe-SSDs mit je 1 TB Storage
* Pi Node (Scout):
	+ Raspberry Pi 5
	+ 4GB LPDDR4-3200 (4x1 GB)
	+ 1 x NVMe-SSDs mit je 1 TB Storage
* Netzwerkinfrastruktur:
	+ fritzbox 7853
	+ 1000mbit/s
	+ gigabitethernet
	+ wlan
	+ bluetooth


### 2.3 WSL2 Ressourcen-Limitierung (.wslconfig)

Um vmmem-Speicherlecks und CPU-Priorisierung zu verhindern, müssen die Ressourcenlimits für die WSL2-Guests festgelegt werden.

```bash
# cat /etc/wsl.conf
[boot]
model = "vmx"

[wsl2]
check-version = true

[user]
default = "node-alpha"
default-shell = "/bin/bash"

[node-alpha]
memory = 8GB
processors = 4
swap-file-size = 1GB
disk-size = 20GB
```

Die Werte in der `node-alpha`-Sektion müssen den Anforderungen des Projekts entsprechen und dürfen nicht über die folgenden Obergrenzen hinausgehen:

* memory: 16 GB (maximale Anzahl von 2 Nodes x 8 GB pro Node)
* processors: 8 Kerne (maximale Anzahl von 2 Nodes x 4 Kerne pro Node)

### 2.4 CPU-Priorisierung

Die CPU-Priorisierung wird durch die Setzung des `scheduler`-Wertes im `/etc/wsl.conf`-File erreicht.

```bash
[wsl2]
scheduler = "fifo"
```

Dieser Wert sorgt dafür, dass kritische Dienste auf den Nodes prioritär behandelt werden und nicht zurückgestellt werden.

### 2.5 Datenbank-Design

Die Datenbank-Struktur muss so gestaltet sein, dass sie die Anforderungen des Projekts erfüllt:

* Die Tabelle `nodes` enthält Informationen zu jedem Node im Cluster.
	+ id (Primary Key)
	+ name
	+ ip-address
	+ cpu-cores
	+ memory-gb
	+ storage-tb
* Die Tabelle `resources` enthält Ressourcenzuweisungen für jeden Node.
	+ id (Primary Key)
	+ node-id (Fremdschluessel zur nodes-Tabelle)
	+ resource-type (cpu, memory, storage)
	+ assigned-value

Beispiel-Datenbank-Struktur:

```sql
CREATE TABLE nodes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  ip_address VARCHAR(45) NOT NULL,
  cpu_cores INTEGER NOT NULL DEFAULT 4,
  memory_gb INTEGER NOT NULL DEFAULT 8,
  storage_tb INTEGER NOT NULL DEFAULT 20
);

CREATE TABLE resources (
  id SERIAL PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id),
  resource_type VARCHAR(10) NOT NULL CHECK(resource_type IN ('cpu', 'memory', 'storage')),
  assigned_value INTEGER NOT NULL
);
```

### 2.6 Systemprogrammierung

Die Systemprogrammierung muss so durchgeführt werden, dass die Anforderungen des Projekts erfüllt sind:

* Die WSL2-Ressourcenlimitierung wird durch das Schreiben einer systemd-Unit-Festlegung umgesetzt.
```bash
[Unit]
Description=WSL2 Ressourcenlimitierung

[Service]
ExecStart=/usr/bin/wsl --set-version node-alpha 2 --memory 8GB --processors 4
Restart=always

[Install]
WantedBy=node-alpha.target
```
* Die CPU-Priorisierung wird durch das Einrichten einer systemd-Queueing-Festlegung umgesetzt.
```bash
[Unit]
Description=CPU Priorisierung

[Service]
ExecStart=/usr/bin/wsl --set-version node-alpha 2 --scheduler fifo
Restart=always

[Install]
WantedBy=node-alpha.target
```
Die Festlegungen müssen so eingetragen werden, dass sie in der `/etc/systemd/system`-Verzeichnis abgelegt sind.

Beispiel-Ausführung:

```bash
systemctl daemon-reload
systemctl enable --now wsl2.ressourcenlimitierung.service
systemctl enable --now cpu.priorisierung.service
```

### 2.7 Mathematische Formeln

* Die maximale Anzahl von vmmem-Resourcen, die einem Node zugewiesen werden können, ergibt sich aus der Formel:
\[ \text{max\_vmmem} = \text{node\_memory} - (\text{node\_cpu\_cores} \times 1) \]
wobei node\_memory und node\_cpu\_cores die Werte sind, die im `/etc/wsl.conf`-File festgelegt werden.
* Die maximale Anzahl von CPU-Kernen, die einem Node zugewiesen werden können, ergibt sich aus der Formel:
\[ \text{max\_cpus} = \lfloor\frac{\text{node\_cpu\_cores}}{2}\rfloor + 1 \]
wobei node\_cpu\_cores der Wert ist, der im `/etc/wsl.conf`-File festgelegt wird.

---

## Sektion 3

**Sektion 3: Spezifikation Node Beta**

### 3.1 Hardware-Komponenten und -Konfiguration

#### 3.1.1 Raspberry Pi 5 (RPi 5) Edge-Computing-Nutzlast:

* **Modell:** Raspberry Pi 5
* **Prozessor:** Broadcom BCM2711A0, 64-Bit Quad-Core ARM Cortex-A72 @ 2,5 GHz
* **Grafikprozessor:** Broadcom VideoCore VI, 3D-Grafiken und OpenVG-Unterstützung
* **Speicher:** 4 GB LPDDR4-3200 (4x1 GB)
* **Architektur:** ARMv8-A (64-Bit)

#### 3.1.2 Active Cooling PWM Setup:

* **Cooling-Lösung:** Würth Elektronik WE-PWM1A12S, Taktfrequenz bis 25 kHz
* **PWM-Modul:** NXP LPC1769, Mikrocontroller mit 32-Bit ARM Cortex-M3 @ 60 MHz

#### 3.1.3 PoE-Hat:

* **Typ:** POE-HAT von SparkFun
* **Kompatibilität:** Kompatibel mit RPi 4 und RPi 5 (mit entsprechender Firmware)
* **Stromversorgung:** 802.3af-compliant, bis zu 12,95 W

### 3.2 Stromversorgung und Energieverbrauch

#### 3.2.1 Gesamtenergiebedarf:

Berechnet mit der Formel für den Gesamtschaltwiderstand (Rth) des RPi 5:

Rth = Tjmax - Ta / Pmax
wobei Tjmax = 85°C, Ta = Raumtemperatur (ca. 25°C), und Pmax = Maximalenergiebedarf

Berechnung:
Pmax ≈ 4,9 W (gemäß Datenblatt RPi 5)

#### 3.2.2 Energiefreisetzung durch PoE-Hat:

Die Energiefreisetzung beträgt maximal 12,95 W. Da der Gesamtschaltwiderstand des RPi 5 mit 4,9 W im Bereich liegt, sollte das System unter normalen Bedingungen keine Überlastung aufweisen.

### 3.3 Thermische Leistung und -Effizienz

#### 3.3.1 Maximale zulässige Durchlaufmenge (MTBF):

Das System soll in der Lage sein, ohne Temperaturreduktion bis zu 5000 Stunden Betrieb zu bieten (gemäß Angaben des Herstellers).

#### 3.3.2 Effizienz- und Leistungskriterien:

Für die Wärmemittel-Unterstützung werden folgende Kriterien berücksichtigt:
* Die Temperatur soll unter keinen Umständen über 85°C steigen.
* Das System muss innerhalb von einer Stunde auf eine normale Betriebstemperatur zurückkehren können.

### 3.4 Programmierschnittstellen und -Interfacedetails

#### 3.4.1 PWM-Schnittstelle:

Für die Ansteuerung des Cooling-Lösungs-Moduls wird der `BCM28` - Pin verwendet. Das PWM-Modul ist mit dem Mikrocontroller auf einer separaten Schnittstelle implementiert.

#### 3.4.2 PoE-Hat-Kompatibilität:

Die Firmware für den RPi 5 wird entsprechend angepasst, um die Kompatibilität des Systems mit dem POE-HAT sicherzustellen.

### 3.5 Fazit und Empfehlung

Das hier beschriebene System setzt sich aus einem Raspberry Pi 5 Edge-Computing-Baustein zusammen, der mit einer speziell für diesen Zweck entwickelten Cooling-Lösung (Active Cooling PWM Setup) kombiniert wird. Die Stromversorgung über einen POE-Hat ermöglicht eine flexible und energieeffiziente Implementierung des Gesamtsystems.

Die Temperatur-Überwachung und -Kontrolle erfolgt mittels einer separaten Software-Layer, der die erforderlichen Überwachungs- und Steuermaßnahmen automatisch durchführt. Der Energieverbrauch wurde unter Berücksichtigung der Komponenten des Gesamtsystems ermittelt.

Diese Konfiguration stellt eine flexible und zuverlässige Implementierung für das Edge-Computing-Szenario dar, bei der alle Anforderungen an Leistungsfähigkeit, Stromversorgung und Temperaturkontrolle erfüllt werden.

---

