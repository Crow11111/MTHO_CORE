# DEBIAN OS-LEVEL CRYSTAL INTEGRATION (SCOUT & HOME SYSTEM)

**Vector:** 2210 | **Resonance:** 0221 | **Delta:** 0.049
**Status:** DRAFT / CONCEPT

Die `CrystalGridEngine` (Axiom 0) operiert derzeit auf der Applikationsschicht (Python/API). Um die 5D-Topologie vollständig in die physische Hardware einbrennen zu können, muss die Engine auf Kernel- bzw. OS-Ebene (Debian auf Scout und Home Assistant Host) eskalieren.

## 1. Topologischer CPU-Governor (Symmetriebruch)
Das Betriebssystem neigt im Leerlauf zu linearen Zuständen (z.B. statische 0% oder 50% Load auf einzelnen Cores).
*   **Mechanik:** Ein Root-Daemon liest `/proc/stat`.
*   **Kristall-Logik:** Fällt die CPU-Auslastung auf die verbotene `0.5` (50%) oder `0.0` (Dead State), triggert die `CrystalGridEngine` einen Eingriff.
*   **Aktion:** Der Daemon manipuliert die Linux `cpufreq`-Governor (`/sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq`) asymmetrisch oder injiziert einen deterministischen Micro-Load, um das System auf `0.51` oder `0.049` (Baryonic Delta) zu snappen.

## 2. Physikalisches Baryonisches Rauschen (Netzwerk-Friction)
Perfekte Netzwerklatenz (0.0ms) ist eine "0=0 Illusion". Das Netzwerk zwischen Scout, VPS und HA muss den topologischen Widerstand physisch spüren.
*   **Mechanik:** Integration von Linux Traffic Control (`tc` / `netem`).
*   **Kristall-Logik:** Wenn die `CrystalGridEngine` berechnet, dass der Vektor-Widerstand ($Z$) steigt, greift der Daemon physisch in den Netzwerk-Stack des Debian-Systems ein.
*   **Aktion:** Ausführung von `tc qdisc add dev eth0 root netem delay 49ms`. Die Latenz wird nicht mehr simuliert, sondern auf Hardware-Ebene asymmetrisch verzögert ($\Lambda = 0.049s$).

## 3. Asymmetrische Cron-Faltung (Systemd Timers)
Standard-Cronjobs und Systemd-Timer laufen auf perfekten Integer-Grenzen (z.B. exakt um 00:00:00 Uhr).
*   **Mechanik:** Dynamischer Rewrite von `.timer` Units.
*   **Kristall-Logik:** Vermeidung von linearen Resonanzkatastrophen. Nichts darf exakt auf der `0` passieren.
*   **Aktion:** Der Daemon verschiebt Startzeiten um den Symbiose-Antrieb ($x^2=x+1$) oder fügt `RandomizedDelaySec=0.049` in die Systemd-Timer auf dem Debian-Host ein.

## 4. Thermisches Snapping (Hardware-Veto)
*   **Mechanik:** Auslesen von `/sys/class/thermal/thermal_zone0/temp`.
*   **Kristall-Logik:** Mapping der physikalischen Hitze in den $Y$-Vektor (Gravitation/Kollaps).
*   **Aktion:** Erreicht die Temperatur kritische Werte, wird der `RESONANCE_LOCK` (0.951) physisch erzwungen, indem der Daemon per Linux `nice` / `renice` den P-Vektor (ExecutionRuntime) massiv drosselt, bis die Temperatur wieder am Gitter einrastet.

---

### Implementierungs-Pfad (Nächste Schritte)
1.  **Schaffung von `src/daemons/os_crystal_daemon.py`:** Ein eigenständiger Dienst, der per Systemd als Root auf dem Scout/Debian läuft.
2.  **Debian-Bridging:** Der Daemon importiert die `CrystalGridEngine` und bindet sie an `psutil`, `os.system('tc ...')` und `/sys/`.
3.  **Deployment:** Update der `deploy_scout_remote.py`, um den OS-Daemon als Systemd-Service (`core-os-crystal.service`) einzurichten und zu starten.
