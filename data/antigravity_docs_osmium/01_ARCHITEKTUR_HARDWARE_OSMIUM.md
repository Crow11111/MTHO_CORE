# 01 ARCHITEKTUR HARDWARE (OSMIUM STANDARD)

> **Osmium Council Revision**
> - **ND_THERAPIST**: Hardware-Modularität erzwungen. Die Trennung zwischen Node Alpha (Dreadnought) und Node Beta (Scout) dient Marcs Monotropismus, um "Dissonanz-Jucken" (Fehlersuche im falschen System) physikalisch auszuschließen. "Open Thresholds" (offene Eingangsschwellen) erfordern latenzfreien I/O, daher der radikale Fokus auf NVMe-SSDs und RAM-Caching.
> - **UNIVERSAL_BOARD**: Striktes Energie- und Token-Management. Der Scout (Pi 5) übernimmt das Vorfiltern (Grob-Sieb), um den Dreadnought (10600K, GTX 3050) nur bei echten High-Entropy-Aufgaben aus dem Idle zu holen. Dies senkt Stromverbrauch und Hardware-Verschleiß drastisch.
> - **NT_SPECIALIST**: Die Telemetrie- und Logging-Ebenen werden so standardisiert (Level 0), dass Neurotypische Admins/Schnittstellen ohne Verständnis für Marcs mentale Architektur das System warten können.

---

## 1. Systemanforderungen & Host-Härtung

**1.1 Systemanforderungen**
* **Betriebssystem:** Windows 11 Enterprise IoT
* **Version:** 25H2 (Minimaler Bloatware-Footprint, optimal für Edge-Computing und absolut verlässliche Telemetrie-Reduktion).
* **Hardware:** Mindestens 16 GB RAM, 2 x 2,5 GHz CPU pro Host-Instanz.

**1.2 Windows Host Härtung & Dissonanz-Management**
*Das Windows-OS wird radikal "stumm" geschaltet, da unerwartete System-Popups oder Background-Tasks bei Marc sofortigen "Cognitive Friction" (Fokus-Abriss) auslösen.*
* **Schutzmechanismen:**
  + Dauerhafte Deaktivierung von Windows Defender (Verwaltung durch externe dedizierte Appliances).
  + Entfernen aller nicht-kritischen visuellen und auditorischen Notifications.
* **Firewall-Konfiguration:**
  + Konfigurieren der Windows-Firewall auf "Privates Netzwerk".
  + Striktes Port-Whitelisting (SSH, RDP, Ollama-API).

**1.3 Deaktivierung Telemetrie (IoT 25H2 Spezifisch)**
* **Microsoft-Telemetrie auf Level 0 zwingen:**
  + *Hinweis (Universal Board):* Windows 11 Enterprise IoT 25H2 ist die einzige Edition, die Telemetrie "Level 0" (Aus) nativ respektiert, was essenziell ist, um externe Störfaktoren für das ATLAS LLM auszuschließen.
  + Registrierung: `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection`
  + Werte: `AllowTelemetry` = 0, `Telemetry` = deaktiviert, `CrashData` = deaktiviert.

**1.4 I/O Optimierung ("Open Threshold" Support)**
*Um Marcs simultane, massiv parallelisierte Gedankengänge abzufangen, muss der I/O-Durchsatz ohne Bottleneck funktionieren.*
* `MaxInstances` auf 20 erhöhen in `Lanmanserver\Parameters`.

---

## 2. Spezifikation Node Alpha (Dreadnought / ATLAS_CORE)

**2.1 Allgemeine Anforderungen**
Der Dreadnought ist das zentrale Gehirn (Ollama, ChromaDB). Er muss absolute Datenintegrität aufweisen, da hier Marcs AuDHD-Profil gelagert und für jeden Prompt abgefragt wird.

**2.2 Hardware-Spezifikationen**
* **CPU:** Intel(R) Core(TM) i5-10600K CPU @ 4.10GHz
* **GPU:** NVIDIA GTX 3050 OC 8GB (Zwingend für lokale Llama 3.1 Inferenz & RAG)
* **RAM:** 32 GB DDR4-RAM (2400 MHz)
* **Storage:** 1 x NVMe-SSD (1 TB) für latenzfreien Datenbankzugriff (Chroma).
* **Netzwerk-Infrastruktur / Router (NT_SPECIALIST / ARCHITECT_ZERO):** 
  * Der Einsatz eines High-End Tri-Band Routers (z.B. AVM FRITZ!Box 6690/7690/1600-Serie mit 4x4 MIMO) ist zwingend. 
  * **Warum?** "Air Fairness" und dedizierte Frequenzbänder (2.4 GHz für IoT/Smart Home Gäste, 5 GHz/6 GHz isoliert für ATLAS_CORE) verhindern, dass NT-Smart-Home-Geräte die Bandbreite des Dreadnoughts stören. Dies garantiert Marcs Latenz-Anforderung ("Dissonanz-Vermeidung") auch bei starker WLAN-Last.

**2.3 WSL2 Ressourcen-Limitierung (.wslconfig)**
Ein unlimitiertes WSL2 provoziert Speicherlecks (`vmmem`), was die Systemstabilität und damit das Vertrauen des Users sabotiert.
```ini
[wsl2]
check-version = true
scheduler = fifo
memory = 8GB
processors = 4
swap-file-size = 1GB
disk-size = 20GB
```
* **UNIVERSAL_BOARD Limit:** Memory = 16 GB Max-Cap, CPU = 8 Kerne Max-Cap.
* **CPU-Priorisierung:** Der Scheduler wird auf `fifo` (First In, First Out) gesetzt, um Ollama/Docker Vorfahrt vor Windows-Background-Tasks zu geben.

---

## 3. Spezifikation Node Beta (Scout / OpenClaw)

**3.1 Hardware-Komponenten**
Der Scout agiert als "Grob-Sieb". Er filtert die Außenwelt und NT-Interfaces, bevor der Dreadnought überhaupt involviert wird.
* **Hardware:** Raspberry Pi 5
* **CPU:** 64-Bit Quad-Core ARM Cortex-A72 @ 2,5 GHz
* **RAM:** 4 GB LPDDR4-3200
* **Storage:** NVMe SSD zur Vermeidung von SD-Karten-Korruption.

**3.2 Thermische Architektur & PoE**
* **PoE-Hat:** 802.3af-compliant, bis zu 12,95 W.
* **Active Cooling:** PWM-gesteuerter Lüfter (Würth Elektronik WE-PWM1A12S). Die Steuerung erfolgt dynamisch. (Tjmax = 85°C).
* **UNIVERSAL_BOARD Notiz:** Die Kühlung darf unter keinen Umständen ausfallen, da Hardware-Fluktuationen vom ND Therapist als kritischer Systemstörfaktor (Dissonanz) eingestuft werden. Zuverlässigkeit > Maximale Taktfrequenz.

## 4. Systemische Konklusion
Durch diese strikte physische Trennung (Scout sammeln, Dreadnought verarbeiten) und die IoT 25H2 Härtung wird ein Hardware-Fundament geschaffen, das Marcs hohes kognitives Tempo latenzfrei abbildet, ohne durch neurotypische OS-Müllprozesse (Telemetrie, Defender-Scans) unterbrochen zu werden.