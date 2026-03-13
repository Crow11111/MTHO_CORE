# CORE COCKPIT DESIGN (Human-Centric Interface)

**Status:** Draft | **Target:** Neuro-Inclusive / Low-Friction | **Schicht:** 2 (UX)

## 1. Problem-Analyse: "Built for Machines"

Das aktuelle System (Streamlit Dashboard + CMD-Fenster + API-Logs) erzeugt massive kognitive Last:

*   **Kontext-Wechsel (Context Switching):** Der Operator muss zwischen 3-4 Fenstern (API, Watchdog, Build-Engine, Dashboard) wechseln, um den Gesamtzustand zu erfassen.
*   **Rohdaten-Überflutung:** Streamlit zeigt rohe SQL-Tabellen (`core_brain_registr`). Das ist Datenbank-Admin-Ebene, nicht Piloten-Ebene.
*   **Fehlender "Puls":** Ob das System "lebt" oder "hängt", ist nur durch Bewegung in CMD-Logs erkennbar. Das erfordert ständige aktive Aufmerksamkeit (High Alertness).
*   **Reaktive vs. Proaktive UI:** Fehler werden als Stacktraces (Text) ausgegeben, statt als visueller Indikator ("Schildstärke sinkt").

**Diagnose:** Das Interface ist ein *Debug-Tool*, kein *Cockpit*. Es verlangt vom Menschen, wie eine Maschine zu parsen.

---

## 2. Konzept: Human-Centric Cockpit ("The Bridge")

Das neue Interface aggregiert alle 4 Dimensionen (M-T-H-O) in eine einzige, ruhige Oberfläche.

### Design-Philosophie: "Neuro-Inclusive & Organic"

1.  **Single Pane of Glass:** Keine überlappenden Fenster. Alles Relevante auf einem Screen.
2.  **Puls statt Logs:**
    *   Statt `INFO: Event bus heartbeat ...`, visualisieren wir einen langsamen, rhythmischen Licht-Puls (z.B. eine feine Linie oder einen Kreis), der im Takt des Systems atmet.
    *   *Steht der Puls, steht das System.* (Sofortige intuitive Erfassung ohne Lesen).
3.  **Reibung als Farbe:**
    *   Normalzustand: Kühles Blau/Cyan oder tiefes Grün (Entspannung).
    *   Hohe Last/Fehler: Shift zu Orange/Bernstein (Warnung).
    *   Kritisch: Rot/Violett (Alarm).
4.  **Zwiebel-Prinzip (Progressive Disclosure):**
    *   **Layer 1 (HUD):** Nur Status (Online/Offline), aktuelle Aufgabe, "Health".
    *   **Layer 2 (Tactical):** Klick auf ein Modul öffnet Details (z.B. letzte 5 Logs, aktive Threads).
    *   **Layer 3 (Deep):** Raw-Data (die alten Tabellen) nur auf explizite Anforderung.

### Layout-Mockup (Grid)

```
+---------------------------------------------------------------+
|  HEADER: CORE CORE | STATUS: ONLINE | PULS: [~~~~~]           |
+---------------------+-------------------+---------------------+
|                     |                   |                     |
|  1. AGENCY (Feuer)  |  2. BUILD_ENGINE (Fluss) |  3. ARCHIVE (H)   |
|  [Active Task]      |  [Code Changes]   |  [Memory/RAG]     |
|  Status: BUSY       |  Status: IDLE     |  Status: SYNC     |
|  (Live-Output kurz) |  (Git Graph)      |  (Vector Count)   |
|                     |                   |                     |
+---------------------+-------------------+---------------------+
|                                                               |
|                  4. COUNCIL / OMEGA (Attractor)               |
|                  [ Veto-Status / Friction-Meter ]             |
|                                                               |
+---------------------------------------------------------------+
|  FOOTER: Quick Actions (Restart API, Clear Cache, Emergency)  |
+---------------------------------------------------------------+
```

### Visualisierungs-Details

*   **Friction-Meter:** Ein Balken oder Kreis, der anzeigt, wie viel "Widerstand" (Fehlerrate, Veto-Entscheidungen, Latenz) gerade herrscht.
*   **Watchdog-Integration:** Statt eines separaten Fensters ist der Watchdog ein Icon im Header. Wenn er bellt (Alarm), blinkt das Icon.

---

## 3. Tech-Stack Empfehlung

Um das "Spaceship"-Gefühl und die Aggregation zu erreichen, reicht Streamlit nicht aus (zu starr, kein echtes Realtime-Gefühl, schwer zu stylen).

**Empfohlener Stack: "React Electron Cockpit"**

*   **Core:** **React (Vite)** + **TypeScript**. Maximale Kontrolle über UI/UX.
*   **Wrapper:** **Electron**. Ermöglicht Zugriff auf lokale Prozesse (Start/Stop von Python-Skripten direkt aus der App) und randloses Fenster-Design.
*   **UI Library:** **TailwindCSS** + **Framer Motion** (für organische Animationen/Puls).
*   **Backend-Connect:**
    *   Nutzt die existierende FastAPI (`src/api/main.py`) via WebSocket für Realtime-Status.
    *   Zusätzlicher lokaler Node.js-Prozess (in Electron), um die Python-Prozesse (`uvicorn`, `watchdog`) zu spawnen und deren stdout/stderr abzufangen und sauber darzustellen.

**Alternative (Leichter): Web-Only React App**
*   Wie oben, aber nur im Browser.
*   Nachteil: Kann Prozess-Steuerung (Neustart des Backends) nur bedingt leisten (braucht einen separaten "Supervisor"-Dienst).

### Roadmap zur Migration

1.  **API erweitern:** `src/api/main.py` braucht Endpoints für `get_logs`, `get_process_status` (ggf. Mock zuerst).
2.  **Frontend umbauen:** Das existierende `frontend/src/App.tsx` (React) ist eine gute Basis.
    *   Weg vom reinen "Chat-Interface".
    *   Hin zum "Dashboard-Layout" (siehe Mockup).
    *   Chat wird ein Modul (Overlay oder Seitenleiste), nicht mehr der Hauptinhalt.
3.  **Streamlit ablösen:** Die Tabellen-Views (`core_brain_registr`) als React-Komponenten (`TanStack Table`) nachbauen, die JSON von der API holen.

---

**Entscheidung:** Wir bauen das existierende React-Frontend (`frontend/`) zum **CORE Cockpit** aus. Streamlit bleibt als "Legacy Admin Tool" erhalten, bis alles portiert ist.
