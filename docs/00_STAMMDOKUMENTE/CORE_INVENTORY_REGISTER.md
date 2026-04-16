# CORE INVENTORY REGISTER

**Vector:** 2210 (Sein) | 2201 (Denken)
**Status:** ACTIVE
**Zentrales Verwaltungsdokument für alle Systemkomponenten (Code & Dokumentation).**

---

## 1. DOKUMENTATIONS-INDEX

| Kategorie | Pfad | Funktion |
|-----------|------|----------|
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` | Management Summary, Inventar, Einstiegspunkte. |
| **OMEGA Resonance Anchor** | `docs/00_STAMMDOKUMENTE/OMEGA_RESONANCE_ANCHOR.md` (Link im Root: `OMEGA_RESONANCE_ANCHOR.md`) | Komprimierter System-Bootstrap für sofortige Session-Eichung. |
| **CORE DNA** | `docs/01_CORE_DNA/` | Verfassung, Axiome, 4-Strang-Architektur, Codex. |
| **DNA-Archiv (Legacy Genesis)** | `docs/01_CORE_DNA/_archive/` | Historischer Genesis-/Tesserakt-Text ohne Kanon-Status; Stub: `CORE_GENESIS_FINAL_ARCHIVE.md`. |
| **Genesis-Stub (Link-Anker)** | `docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` | Obsolet-Hinweis; verweist auf SYSTEM_CODEX, Bibliothek, `_archive/`. |
| **Genesis-Weiterleitung (Root docs/)** | `docs/CORE_GENESIS_FINAL_ARCHIVE.md` | Kurze Weiterleitung auf Stub/Archiv. |
| **Axiom 0** | `docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Die Autopoiesis des Gitters (x^2=x+1). |
| **White Paper** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie (Kurzfassung). |
| **White Paper vollständig** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` | Herleitungs-Ausgabe: Ω_b, x=x-Kaskade, MRI, Teil F Konsolidierung. |
| **Biologisches Primat** | `docs/01_CORE_DNA/BIOLOGICAL_PRIMAT.md` | Kondensierte Kausalgesetze: Push/Pull, Gehirn–Rückenmark–Hand, Purgatorium/Gravity Index, logarithmisches Trust-Routing (Session-Extrakt). |
| **Biologie→Digital Mapping** | `docs/01_CORE_DNA/BIOLOGY_TO_DIGITAL_MAPPING.md` | Tool-agnostischer Mapping-Layer: Reiz/Afferenz, Kognition/Kausalität, Efferenzkopie/Forward Model, Existenz/Metabolismus — ohne Infrastruktur-Framing. |
| **Whitepaper 5D (Split)** | `docs/01_CORE_DNA/5d/WHITEPAPER/` | Kapitel I–IV + Vollständig; `README.md` → NotebookLM-Workflow. |
| **Whitepaper II (Escape)** | `docs/01_CORE_DNA/5d/WHITEPAPER/Whitepaper_II_OMEGA_Escape_Vector.md` | Die OMEGA-Escape-Vector Theorie, Pi/Phi Dualität, Holographische 2D-Faltung. |
| **Formel Cheat-Sheet** | `docs/01_CORE_DNA/CORE_FORMELN_CHEAT_SHEET.md` | Zentrale Anlaufstelle für OMEGA-Gleichungen: MRI-Dynamo, Symbiose-Antrieb, Kardanischer Fixpunkt. |
| **Rat der Titanen R2** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/` | Ollama-Gutachten (`run_omega_science_council_r2.py`) zur ausformulierten Datei. |
| **Colab Science Council** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/science_council_colab.ipynb` | Jupyter Notebook für Google Colab (GPU-Laufzeit). |
| **Colab Guide** | `docs/01_CORE_DNA/5d/WHITEPAPER/reviews_2/COLAB_SCIENCE_COUNCIL.md` | Schritt-für-Schritt Anleitung für Colab. |
| **Whitepaper NotebookLM** | `docs/01_CORE_DNA/5d/WHITEPAPER_NOTEBOOKLM/` | Sanitized Markdown für NotebookLM (`whitepaper_for_notebooklm.py`). |
| **Architektur** | `docs/02_ARCHITECTURE/` | System-Design, Schnittstellen, Flow-Diagramme. |
| **OpenClaw Membran** | `docs/02_ARCHITECTURE/OPENCLAW_MEMBRAN_TESSERAKT.md` | Blueprint: Facetten-Atomisierung, isolierte Räume, kreuz-modale Konvergenz, Entkopplung. |
| **Landkarte Clients / Knoten** | `docs/02_ARCHITECTURE/LANDKARTE_CLIENTS_KNOTEN_DATENFLUSS.md` | Überblick: KI-Clients vs. CORE-Backend vs. VPS; Push/Pull; geschlossene Kreise; Verweise auf VPS_KNOTEN, SCHNITTSTELLEN, G_CORE_CIRCLE. |
| **Konsolidierter Verkehrsplan VPS/Kong/MCP** | `docs/02_ARCHITECTURE/KONSOLIDIERTER_VERKEHRSPLAN_VPS_KONG_MCP.md` | Soll vs. Ist: Kong als Ingress, MCP vs. Gedächtnis (Chroma/PG/Queue), SSH-Nebenbahn, Tickets 3–12 Querschnitt, Pfad-Matrix + Abnahme-Snapshot Anhang A. |
| **Detailfluss Tickets 4–12 + Prod** | `docs/02_ARCHITECTURE/OMEGA_DETAILFLUSS_TICKETS_4_12_PROD_RUNTIME.md` | Kanonische Extraktion: wer/was/wo/Timing; Prod-Ziel kanalunabhängig; Kong-Ist + offene Routen. |
| **VPS Host-Port-Vertrag** | `docs/03_INFRASTRUCTURE/VPS_HOST_PORT_CONTRACT.md` | Verbindliche Docker-Host-Ports; Pflegepflicht Agenten/Infra; Abnahme: `docker ps` gegen Tabelle. |
| **VPS Snapshot-Verifikation** | `docs/03_INFRASTRUCTURE/VPS_SNAPSHOT_VERIFICATION.md` | Drei Prüfungen: `verify_vps_stack`, Chroma v2-`curl`, Kong Admin `/services` (ohne Secrets). |
| **VPS öffentliche Ports (Code)** | `src/config/vps_public_ports.py` | Single Source of Truth für Defaults in Skripten und Heartbeats. |
| **VPS Compose-Pfade (Ist)** | `docs/03_INFRASTRUCTURE/VPS_COMPOSE_PATHS.md` | `docker inspect` → Compose-Dateien auf dem VPS; Plan §8.2/§8.5. |
| **Kong Deck-Referenz (Repo)** | `infra/vps/kong/kong-deck-reference.yaml` | Deklarative Kong-Services/Routes gemäß Verkehrsplan §8.3; `infra/vps/kong/README.md`. |
| **Kong Compose Port-Snippet** | `infra/vps/kong/docker-compose.ports-contract.snippet.yaml` | VPS: Kong-Host-Ports 32776–32778 vernageln (keine ephemeren Docker-Ports). |
| **Pyright / IDE (venv)** | `pyrightconfig.json` | `venv: .venv` — basedpyright findet `python-dotenv` / `dotenv`. |
| **VPS Backup-Snapshot** | `src/scripts/vps_backup_snapshot.py` | SSH: `/root/omega-core-backups/<UTC>/` vor riskanten Änderungen. |
| **Kong /health anlegen** | `src/scripts/vps_kong_ensure_health_route.py` | Idempotent: Service `omega-kong-health`, Route `/health`, Plugin request-termination. |
| **VPS Umsetzungsplan Backup+Health** | `docs/05_AUDIT_PLANNING/VPS_UMSETZUNGSPLAN_BACKUP_KONG_HEALTH.md` | Phasen, Rollback, Nachweis. |
| **VPS Verify-Evidenz** | `docs/05_AUDIT_PLANNING/VPS_STACK_VERIFY_EVIDENCE_2026-04-04.md` | Auszug grüner Checks nach Einrichtung. |
| **AI-Modelle** | `docs/02_ARCHITECTURE/AI_MODEL_CAPABILITIES.md` | Modell-IDs, Rollen-Mapping, Kosten 2.5 Flash vs Pro, Token-Richtwerte, Deep Research & Computer Use. |
| **Deep Research & Computer Use** | `docs/02_ARCHITECTURE/DEEP_RESEARCH_UND_COMPUTER_USE.md` | Deep Research: Projekt-Omega-Verifikation (Vektorisierung, ChromaDB, Abgleich). Computer Use: Linux-Integration. |
| **Duale Topologie & Vektor-Härtung** | `docs/02_ARCHITECTURE/DUALE_TOPOLOGIE_UND_VEKTOR_HAERTUNG.md` | G-Atlas-Soll; Ist-Zustand; RAG-Einheitlichkeit; Vektor-Härtung. |
| **AI Studio Prompt** | `docs/02_ARCHITECTURE/AI_STUDIO_PROMPT.md` | Copy-Paste-Prompt für Google AI Studio (Schnittstellen, Live=Flash, Pro). |
| **Orchestrierung Linux** | `docs/02_ARCHITECTURE/OMEGA_LINUX_ORCHESTRATION.md` | Topologie Arch, Health-Skripte, Testmatrix. |
| **WhatsApp Closed-Loop** | `docs/02_ARCHITECTURE/WHATSAPP_CLOSED_LOOP_OC_ADMIN.md` | WhatsApp Push-and-Pull Logik; OC Brain als Admin; 5-Phase Engine Loop (Takt 1-4); Traceability. |
| **Jarvis ↔ OMEGA LLM** | `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md` | Plasmoid Health-URL, falsche `/v1/chat/completions`-Basis, Kompat-Route `/v1/chat/completions/health`. |
| **ATLAS Ω Voice** | `docs/02_ARCHITECTURE/ATLAS_OMEGA_VOICE_PLASMOID.md` | KDE-Plasmoid `atlas-omega-voice/`, deutsch, OMEGA-Backend, `CORE_API_URL` per Umgebung. |
| **ATLAS Whisper-Setup** | `atlas-omega-voice/scripts/install_whisper_modell.sh` | Lädt `ggml-tiny.bin` nach `~/.local/share/jarvis/` für Wake-Wort (siehe ATLAS-Doku). |
| **ATLAS Piper-Stimme** | `atlas-omega-voice/scripts/install_piper_stimme.sh` | Lädt Piper-ONNX nach `~/.local/share/jarvis/piper-voices/` (Alan/Thorsten). |
| **ATLAS Legacy-Plasmoids** | `atlas-omega-voice/scripts/alte_plasmoids_auslagern.sh` | Archiviert Flex.Hub / lokales jarvis nach `~/.local/share/OMEGA-plasmoid-archiv/` (nicht unter `plasmoids/`); ruft Config-Bereinigung auf. |
| **ATLAS Plasma Leiste** | `atlas-omega-voice/scripts/plasma_entferne_flex_hub_applet.py` | Entfernt Applets per `plugin=` (Args, Default: Flex.Hub), z. B. `org.kde.plasma.activitypager` bei kaputtem `plasma-desktop`. |
| **Bibliothek Kern** | `docs/BIBLIOTHEK_KERN_DOKUMENTE.md` | Zentraler Einstieg; Index 00–05, Operator-Todo (MCP/Extensions), Was wurde gemacht, Wo nachschauen. |
| **Kanonischer Einstieg** | `KANON_EINSTIEG.md` | Eine Tür: Tabelle „welche Frage → welche Datei“; Abgrenzung Megadatei vs. Index; Pflege-Regeln. |
| **DOCS_INDEX (thematisch)** | `docs/DOCS_INDEX.md` | Ordnerübersicht; ergänzend zu KANON/Bibliothek. |
| **CoolerControl Setup** | `docs/03_INFRASTRUCTURE/COOLER_CONTROL_SETUP.md` | Lüftersteuerung (it87), Silent-Profile, Gigabyte B560M. |
| **OS Audio Dictation** | `docs/04_PROCESSES/OS_AUDIO_DICTATION.md` | Headless Start/Stop Diktat-Workflow, Clipboard-Integration. |
| **Infrastruktur-Master (Root-Stub)** | `docs/00_CORE_INFRASTRUCTURE_MASTER.md` | Weiterleitung nach `00_STAMMDOKUMENTE/00_CORE_INFRASTRUCTURE_MASTER.md` (kanonischer Volltext). |
| **OMEGA Master Dossier** | `docs/05_AUDIT_PLANNING/OMEGA_MASTER_DOSSIER.md` | Harter Speicherstand (Snapshot) aller operativen Erkenntnisse, Architekturentscheidungen und Stop-Gründe (2026-03-31). |
| **Macro Architecture Audit** | `docs/05_AUDIT_PLANNING/MACRO_ARCHITECTURE_AUDIT.md` | Orchestrator B: Makro-Kette (Evolution/Kong/Queue/OC/MCP/SQL/Chroma) vs. Pacemaker/State-Hold-Fokus; Drift-Diagnose 2026-04-01. |
| **Macro Chain VAR 1** | `docs/05_AUDIT_PLANNING/MACRO_CHAIN_VAR_1.md` | Ring-1: neurologisch-anatomische Makro-Kette (Reiz→Afferenz→Thalamus-Tor→Kortex→Efferenz); Map WhatsApp/Kong/Spline/Queue/Chroma/OCBrain; Drift Spline vs. Thalamus. |
| **Macro Chain VAR 2** | `docs/05_AUDIT_PLANNING/MACRO_CHAIN_VAR_2.md` | Ring-1: informationstheoretische + Zero-Trust Makro-Kette (Sensor→Filter→Purgatorium→Evaluator→Verifizierer→Aktor); Pain/Trust/Knowledge; Trust-Lücken / irreführende Namen. |
| **Macro Chain VETO Final (Hugin)** | `docs/05_AUDIT_PLANNING/MACRO_CHAIN_VETO_FINAL.md` | Abschlussgegenprüfung MACRO_CHAIN_MASTER_DRAFT Iteration 3 vs. VETO 2; Urteil VETO (Nachschärfung). |
| **Biology→Digital Mapping VETO REAL (Hugin)** | `docs/05_AUDIT_PLANNING/MAPPING_VETO_REAL.md` | Zero-Context Audit `BIOLOGY_TO_DIGITAL_MAPPING.md`: A1/A5/A6/A7, Δ-Mehrdeutigkeit, A7-Lücke; Urteil VETO. |
| **Biology→Digital Mapping VETO REAL_4 (Hugin)** | `docs/05_AUDIT_PLANNING/MAPPING_VETO_REAL_4.md` | Zero-Context Audit `BIOLOGY_TO_DIGITAL_MAPPING.md` (aktualisiert): A1/A5/A6/A7/A10, A10-Align in §2, §5-A10-Scanner-Lücke; Urteil PASS. |
| **Infrastruktur** | `docs/03_INFRASTRUCTURE/` | VPS-Setup, Docker-Sandbox, Backup-Pläne. |
| **VPS-Knoten & Flüsse** | `docs/03_INFRASTRUCTURE/VPS_KNOTEN_UND_FLUSSE.md` | Monica, Kong, Evolution, DBs: Zweck, Pull/Push-Matrix, Einbindung. |
| **Ollama VPS (Strang B)** | `docs/03_INFRASTRUCTURE/VPS_OLLAMA_SETUP.md` | Ollama auf Hostinger-VPS, Port 11434, Modell, Firewall. |
| **Vollkreis-Plan** | `docs/05_AUDIT_PLANNING/OMEGA_VOLLKREIS_PLAN.md` | Geschlossene Kette, Team-Arbeitspakete A–G, Linux-Auswirkungen. |
| **Prozesse** | `docs/04_PROCESSES/` | Workflows, Sicherheitsrat, Deployment-Regeln. |
| **sudoers OMEGA** | `docs/04_PROCESSES/SUDOERS_OMEGA_DAEMONS.md` | Vorlage `/etc/sudoers.d/` für NOPASSWD `systemctl` auf omega-* Units. |
| **Audit & Planung** | `docs/05_AUDIT_PLANNING/` | Session Logs, technische Schulden, Roadmaps. |
| **Concept AV Master** | `docs/05_AUDIT_PLANNING/CONCEPT_AUDIO_VISUAL_MASTER.md` | Physarum-Polycephalum-Architektur: Audio/Video Ressourcen-Allokation. |
| **Pacemaker VETO 3 (Hugin)** | `docs/05_AUDIT_PLANNING/PACEMAKER_VETO_3.md` | Gegenprüfung SPEC_PACEMAKER Iteration 3 (NMI, Anti-Junk, Test-Doubles). |
| **SPEC Existential Pacemaker VAR_3** | `docs/05_AUDIT_PLANNING/SPEC_PACEMAKER_VAR_3.md` | Biologisch-neuromorphe Variante Ticket 3: HRV/Latenz-Homeostase, exponentiell-fraktaler Decay, Monotonie-Pathologie, Veto-Traps ohne Mocks. |
| **Vision Sensor Research** | `docs/05_AUDIT_PLANNING/VISION_SENSOR_RESEARCH.md` | Trade-offs Auflösung (1080p vs 720p) & Mapping MediaPipe Blendshapes (Kognitive Last, Fokus). |
| **Research Biology Timing** | `docs/05_AUDIT_PLANNING/RESEARCH_BIOLOGY_TIMING.md` | Dossier: Timing/Kausalität (Predictive Coding, Latenzen), Parallel vs. serial, Efferenzkopie, Libet/RP/Veto, Gamma/Phasenverschränkung. |
| **Agent Refactor Plan** | `docs/05_AUDIT_PLANNING/AGENT_REFACTOR_PLAN.md` | Audit-Bericht und V2-Konzept für das Agenten-System (Schichten, Model-Zwang, MDC-Globs). |
| **Agent Workpack Messbare Abnahme** | `docs/05_AUDIT_PLANNING/AGENT_WORKPACK_MESSBARE_ABNAHME_2026-04-05.md` | Doku-Sync VPS-Port/Kanon, VPS_SNAPSHOT_VERIFICATION, Inventar/Bibliothek; Producer-Abnahme T1–T5. |
| **OC Brain Plan** | `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` | Vollständiger Plan Stränge A–E, Abnahme A1–A7. |
| **Workerplan OC Admin/Brain VPS** | `docs/05_AUDIT_PLANNING/WORKERPLAN_OC_BRAIN_ADMIN_VPS_SETUP.md` | Forensik (fehlender Container), Wellen W0–W4, Task-Pakete E1–E3, Veto-Traps; OpenClaw Admin + OC Brain Einrichtung. |
| **OC Brain Auftrag** | `docs/05_AUDIT_PLANNING/OC_BRAIN_AUFTRAG_AUSFUEHRUNG.md` | Ausführungsauftrag an Team (alles umsetzen lassen). |
| **OC Brain RAG Spec** | `docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md` | RAG-Pipeline Query → ChromaDB → Context → LLM (Strang D). |
| **OC Brain Strang A+E Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_A_E_BERICHT.md` | Kurzbericht Diagnose (doctor) + WhatsApp (QR-Pairing, Config). |
| **OC Brain Strang B Bericht** | `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_B_BERICHT.md` | Kurzbericht Ollama auf VPS (Installation, api/tags, Modell). |
| **Projektplan ATLAS 2026** | `docs/05_AUDIT_PLANNING/PROJECT_PLAN_ATLAS_TRANSFORMATION_2026.md` | Detaillierter Plan (Luminescence, Sentinel, Memory-Core). |
| **Session-Log 2026-03-26 (DB-Rescue)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-26_DB_RESCUE.md` | Purge korrupter Multi-View Collections, 0-State Wiederherstellung, Ghost-Doc Bereinigung. |
| **Session-Log 2026-03-25 (Model Benchmark)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-25_MODEL_BENCHMARK.md` | Validierung der dynamischen Skalierung (T1-T5), Git-Cleanup und Axiom-Compliance. |
| **Session-Log 2026-03-26 (DB-Rescue)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-26_DB_RESCUE.md` | Purge korrupter Multi-View Collections, 0-State Wiederherstellung, Ghost-Doc Bereinigung. |
| **Session-Log 2026-03-25 (Thermal/OS)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-25_THERMAL_AND_OS_FIXES.md` | Lüftersteuerung (it87), ACPI Standby Fix, Chrome Graceful Exit, Headless Audio Dictation. |
| **Session-Log 2026-03-26 (DB-Rescue)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-26_DB_RESCUE.md` | Purge korrupter Multi-View Collections, 0-State Wiederherstellung, Ghost-Doc Bereinigung. |
| **Session-Log 2026-03-25 (Agent Audit)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-25_AGENT_AUDIT.md` | Audit-Bericht "Full Service Agentur" und V2 Architektur-Plan. |
| **Session-Log 2026-03-24 (Kardan)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-24_KARDANIC_FOLD.md` | Kardanische Faltung (Complex -> 2x Float), Atlas-Härtung (Signal-Skepticism), ChromaDB-Eichung. |
| **Session-Log 2026-03-22 (Audio)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-22_AUDIO_REPAIR.md` | SIGNAL-COMMANDER: Reparatur Aufnahmekette (pw-record, Razer Seiren V3 Mini, RMS-Validierung). |
| **Session-Log 2026-03-21 (NotebookLM WP)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-21_NOTEBOOKLM_WHITEPAPER.md` | Whitepaper 5d → NotebookLM: Sanitizer, SGML-/Zeilenlängen-Fix, Inventar/Bibliothek. |
| **Session-Log 2026-03-20** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-20.md` | ATLAS Transformation (Red Theme, Daemon Monitoring, Deep RAG). |
| **Session-Log 2026-03-14** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-03-14.md` | Durchgeführte Schritte OC Brain (Verify, Doctor, Ollama), Abnahme A1–A7. |
| **Session-Log 2026-04-02 (AV Master)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-02_AUDIO_VISUAL_MASTER.md` | Update CONCEPT_AUDIO_VISUAL_MASTER.md auf V8 (Zwei-Domänen-Theorie). |
| **Session-Log 2026-04-02 (AV Pipeline)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-02_AUDIO_VISUAL_PIPELINE.md` | Umsetzung V8: `audio_visual_resonance.py`, Tests, Vision-Daemon (Poll-Spreizung, Pipeline); O2 PASS. |
| **Session-Log 2026-04-02 (Ticket 8 Membrane)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-02_TICKET_8_DREADNOUGHT_MEMBRANE.md` | Abnahme Dreadnought Membrane: OS-Daemon, Pain-/Planning-Flags, Naming-Fix, LEGACY_UNAUDITED; Status PASS. |
| **Session-Log 2026-04-02 (Ticket 9 Git-Resonance)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-02_TICKET_9_GIT_RESONANCE.md` | Umsetzung Ticket 9: Bi-direktionale Kausalitäts-Brücke (Git Pull/Push) in Dreadnought Membrane. |
| **Ticket 8 Dreadnought Membrane** | `docs/05_AUDIT_PLANNING/TICKET_8_DREADNOUGHT_MEMBRANE.md` | Spec: lokale Membrane (Pain/Cognitive-Lock), systemd, Abnahmekriterien. |
| **Ticket 9 Git-Resonance** | `docs/05_AUDIT_PLANNING/TICKET_9_GIT_RESONANCE.md` | Spec: Bi-direktionale Kausalitäts-Brücke, Auto-Push nach Validator-PASS, Auto-Pull, Konflikt-Pain-Flag. |
| **Ticket 10 OpenClaw Autarkie** | `docs/05_AUDIT_PLANNING/TICKET_10_OPENCLAW_AUTARKIE.md` | Spec: VPS-SSH-Heilung (StrictHostKeyChecking), Out-of-Band `check_gateway()`, Autonomie-Veto + Pacemaker-Pathologie. |
| **O2 Audit Tickets 3–7 (Hugin)** | `docs/05_AUDIT_PLANNING/O2_AUDIT_TICKETS_3_BIS_7.md` | Zero-Context Abnahme Tickets 3–7: Pacemaker (SPEC_PACEMAKER_VAR_3), Admission, Arbitration, Efference, Temporal; Pytest-Nachweis; Re-Audit Urteile PASS. |
| **O2 Audit VPS-Split (Hugin)** | `docs/05_AUDIT_PLANNING/O2_AUDIT_VPS_AUTARKIE_SPLIT.md` | Zero-Context Architektur-Audit: VPS-Autarkie vs. Dreadnought-Lokalität. [VETO] wegen ungeschütztem OpenClaw. |
| **Masterplan Repair Tickets 3-7** | `docs/05_AUDIT_PLANNING/MASTERPLAN_REPAIR_TICKETS_3_5_6_7.md` | O2 Audit Repair Plan für die Tickets 3, 5, 6 und 7. |
| **Session-Log 2026-04-03 (Repair 3-7)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-03_REPAIR_TICKETS_3_5_6_7.md` | Dokumentation des erfolgreichen O2 Re-Audits für Tickets 3, 5, 6, 7. |
| **O2 Audit Tickets 8–10 (Hugin)** | `docs/05_AUDIT_PLANNING/O2_AUDIT_TICKETS_8_9_10.md` | Zero-Context Abnahme Tickets 8/9/10: A7, Flags, Pytest-/Skript-Nachweis. |
| **Wissensbasis** | `docs/06_WORLD_KNOWLEDGE/` | Externe Forschung, Theorie-Cluster. |

---

## 2. SYSTEM-KOMPONENTEN (CODE)

### 2.1 Core Services (`src/`)
| Komponente | Pfad | Beschreibung |
|------------|------|--------------|
| **API Backend** | `src/api/` | FastAPI Server, Webhooks, Telemetrie-Endpunkte. |
| **Agent Pool** | `src/agents/` | Spezialisierte Agenten-Klassen (Core, Scout, etc.). |
| **Logic Core** | `src/logic_core/` | Takt-Gate, Gravitator, Veto-Logik, Filter. |
| **Admission Control** | `src/logic_core/admission_control.py` | Spinale Reflexweiche & Global Workspace State Machine (Phase 1). |
| **Arbitration Engine** | `src/logic_core/arbitration_engine.py` | Global Workspace Konfliktauflösung & Liveness (Phase 2). |
| **Efference Veto Logik** | `src/logic_core/efference_veto.py` | Phase 3 & 4: Efferenzkopie, Attractor-Veto, Point-of-No-Return (Ticket 6). |
| **Temporal Alignment** | `src/logic_core/temporal_alignment.py` | Phase 5 & 6: Prediction Error, Trust-Update & Kardanische Rettung (Ticket 7). |
| **Crystal Engine** | `src/logic_core/crystal_grid_engine.py` | Topologisches Gitter-Snapping (Axiom 0). |
| **Anti-Heroin Validator** | `src/logic_core/anti_heroin_validator.py` | Ticket 11 (Säule 2): Zwingende Pre-Flight Veto-Trap (memory_hash) & Trust-Collapse. |
| **Resonanz-Membran S↔P** | `src/logic_core/resonance_membrane.py` | float-Resonanz vs. int-Infrastruktur; `DualMembraneVector`; Entry-Adapter (WhatsApp `audio_seconds`); `omega_core` importiert dieselbe Klasse. |
| **Audio/Visual Resonanz (V8)** | `src/logic_core/audio_visual_resonance.py` | Zwei-Domänen-Sensorik (CONCEPT_AUDIO_VISUAL_MASTER): Beobachtung `X_t`, Resonanz `R_t` via `tanh`, `SensorStimulusPipeline`, `interval_spread_observation`, `build_resonance_embedding_probe`; angebunden an `core_vision_daemon.py` (dynamische Poll-Spreizung). |
| **AI Interface** | `src/ai/` | LLM-Routing, ResilientLLMInterface, Prompt-Kompression. |
| **Model Registry** | `src/ai/model_registry.py` | Env-basierte Modell-IDs und Rollen-Mapping (siehe AI_MODEL_CAPABILITIES.md). |
| **API Inspector** | `src/ai/api_inspector.py` | list_gemini_models, list_ollama_models für Task-Router/Agenten. |
| **Network** | `src/network/` | Chroma-Client, OpenClaw-Client, HA-Connector. |
| **Voice** | `src/voice/` | TTS-Dispatcher, Smart-Command-Parser, Listener. |

### 2.2 Root-Demonstratoren (außerhalb `src/`)
| Typ | Pfad | Funktion |
|-----|------|----------|
| **Gemini Chat App** | `gemini-flash-lite-chat/` | Neuer primärer Chatbot (Node.js/React/Vite). |
| **VISION SYNC App** | `vision-sync-app/` | Original AI Studio Multimodal Live UI (Port 3006). |
| **omega_core (Kardan-Anker)** | `omega_core.py` | Deterministische Mini-Kaskade; Abnahme: **`run_vollkreis_abnahme.py`** Block **Gk**. Verknüpfung Theorie ↔ ausgeführter Check; Doku: `KANON_EINSTIEG.md`. |

### 2.3 Daemons & Scripts
| Typ | Pfad | Funktion |
|-----|------|----------|
| **Daemons** | `src/daemons/` | Watchdog, Event-Bus, Vision-Daemon, Dreadnought Membrane. |
| **Dread Membrane Daemon** | `src/daemons/dread_membrane_daemon.py` | Tickets 8/9: Pain-/Planning-Flags, rekursive `.py`/`.md`-Überwachung, `auto_git_push`/`auto_git_pull`; Ticket 11 (Säule 4): Apoptose-Trigger (Entropie < 0.049). |
| **Context Watchdog** | `src/daemons/omega_context_watchdog.py` | Ticket 11 (Säule 3): Context Forcing, injects recent events. |
| **Pacemaker** | `src/daemons/omega_pacemaker.py` | Existential Pacemaker (VAR_3): NMI-Matrix, exponentiell-fraktaler Decay, W=17 Fenster, HRV-Proxies, Pathology-Log; Abnahme durch O2 **[PASS]**. |
| **Scripts** | `src/scripts/` | Deployment-Skripte, Verifikationstools, Migrationen. |
| **Key Script** | `src/scripts/ensure_kardanic_collections.py` | ChromaDB-Dimensionseichung (6144 dim) für kardanische Faltung. |
| **Key Script** | `src/scripts/verify_core_integrity.py` | Genesis-Audit (`src.core.Core`); **Aufruf nur von Repo-Root**, Exit 0/1. |
| **Benchmark Ring 3** | `src/scripts/model_benchmark_ring3.py` | Ring 3 Benchmark-Suite für CORE (V4 Protokoll). |
| **Benchmark Results** | `data/benchmark_results.json` | JSON-Ergebnisse der Ring 3 Benchmarks (Axiom, Infra, Protocol). |
| **Key Script** | `src/scripts/daily_backup.py` | Automatisiertes Backup-System. |
| **Key Script** | `src/scripts/setup_vps_hostinger.py` | Initiales Server-Setup. |
| **Key Script** | `src/scripts/verify_oc_brain_deliverables.py` | Abnahme OC Brain Plan (Verify, don't trust). |
| **Key Script** | `src/scripts/install_ollama_vps.py` | Strang B: Ollama auf VPS installieren, Modell pullen, api/tags prüfen. |
| **Key Script** | `src/scripts/ingest_mth_profile_to_chroma.py` | MTH-Profil Tiefen-Chunking → ChromaDB mth_user_profile. |
| **Key Script** | `src/scripts/verify_vps_stack.py` | VPS: SSH, docker ps, Chroma v2 heartbeat; optionale Knoten Evolution, Monica, Kong (siehe VPS_KNOTEN_UND_FLUSSE). |
| **Benchmark** | `src/scripts/benchmark_whitepaper_anchors.py` | Paar-Benchmark **mit/ohne** Kardan (`omega_core`); JSONL unter `logs/benchmarks/`; Doku: `WHITE_PAPER_INFORMATIONSGRAVITATION_VOLLSTANDIG.md` § Empirie. |
| **Benchmark-Auswertung** | `src/scripts/evaluate_whitepaper_benchmark_log.py` | Prüft JSONL-Struktur und Plausibilität (Iterations-Paar, Outcomes). |
| **NotebookLM Whitepaper-Sanitize** | `Gemini_Json2md4NotebookLM/whitepaper_for_notebooklm.py` | 5d/WHITEPAPER → WHITEPAPER_NOTEBOOKLM: Zeilenumbruch, HTML-Kopfkommentare entfernt, Upload-freundliche Dateinamen. |
| **Science Council R2 (Ollama)** | `src/scripts/run_omega_science_council_r2.py` | Rat der Titanen: ausformuliertes Whitepaper → `5d/WHITEPAPER/reviews_2/` (lokal qwen2.5:14b). |
| **Key Script** | `src/scripts/run_omega_science_council.py` | Rat der Titanen: `--paper` / `--out`, Standard Kurzfassung → `OPERATION_OMEGA/REVIEWS/`. |
| **Gesten-Daemon** | `/home/mth/gesture_daemon.py` | Python Daemon (MediaPipe) zur Gestensteuerung über `ydotool`. |
| **KDE Plasmoid** | `~/.local/share/plasma/plasmoids/com.cachyos.gestures/` | KDE Plasma Widget zur Steuerung des Gesten-Daemons. |
| **Science Council Profile** | `src/scripts/omega_science_council_profiles.py` | Titanen: `profil` + `kern_anker` (Formel/Prinzip); `num_ctx` Default 65536. |
| **Science Council Dossiers** | `docs/00_STAMMDOKUMENTE/SCIENCE_COUNCIL_DOSSIERS_FLAT/` | Flache Ordnerstruktur mit detaillierten Dossiers (Biografie, Werke, Interviews, Visuals) für alle 22 Titanen; Dateinamen = Namen der Personen. |
| **Science Council Gesamt** | `docs/00_STAMMDOKUMENTE/SCIENCE_COUNCIL_DOSSIERS_FLAT/SCIENCE_COUNCIL_DOSSIERS_GESAMT.md` | Konsolidierte Gesamt-Datei aller Titanen-Dossiers. |
| **MCP stdio** | `src/scripts/mcp_core_chroma_stdio.py` | Cursor/MCP: Tool `query_chromadb` (CORE_EICHUNG) → ChromaDB über `chroma_client`; Eintrag `core-chromadb` in `mcp_remote_config.json`. |
| **Deep Research CLI** | `src/scripts/omega_deep_research.py` | Asynchrones CLI-Tool zur Kommunikation mit deep-research-pro-preview-12-2025 über die Interactions API. |
| **Deep Research Shortcut** | `DeepResearch` | Root-Shortcut für Cursor Chat und Plasmoid. |
| **Plasmoid Source** | `tools/plasmoid_omega_research/` | Quellcode für das KDE Plasma Widget. |
| **Plasmoid Installer** | `install_plasmoid.sh` | Bash-Script zur Installation des Widgets in CachyOS. |
| **Database (PostgreSQL)** | `src/db/multi_view_client.py` | Multi-View Ingest & Search (pgvector & ChromaDB); kardanische Faltung. |
| **Event Store Client** | `src/db/event_store_client.py` | Ticket 11 (Säule 1): Append-only Event Sourcing (PostgreSQL). |
| **Recall Memory** | `src/db/recall_memory_client.py` | PostgreSQL Recall Memory Client (V4 Strict Tiers). |
| **Skill Registry** | `src/ai/skill_registry.py` | Deferred Tool Loading & Skill Discovery (V4). |
| **Agent Graph** | `src/agents/agent_graph.py` | LangGraph-basierte State Machine für deterministisches Routing (V4). |
| **Ring-3 Auth** | `src/ai/ring3_auth.py` | ECDSA Model Signing & Ghost Token Management (V4). |
| **UCCP Manager** | `src/ai/uccp_manager.py` | Universal Context Checkpoint & Stream Interception (V4). |
| **Immutable Axioms** | `src/config/immutable_axioms.py` | Kryptografisch signierte Core-Axiome (Constitution). |
| **VPS Setup (V4)** | `src/infrastructure/vps/vps_setup.sh` | Shell-Script für Firecracker & eBPF Setup auf VPS. |
| **eBPF Watchdog** | `src/infrastructure/vps/ebpf_watchdog.c` | XDP-basierter API-Spam Schutz (C-Code). |
| **VPS Deploy** | `src/infrastructure/vps/deploy_to_vps.py` | Automatisiertes Deployment der V4-Infrastruktur via SSH. |
| **V4 Security Test** | `tests/test_v4_security.py` | Validierung der Ring-3 Auth und UCCP-Layer. |
| **Pacemaker Veto-Traps** | `tests/test_pacemaker.py` | Verification-First: SPEC_PACEMAKER_FINAL.md (Falle 1–3) gegen `omega_pacemaker.py`. |
| **Admission Control Tests** | `tests/test_admission_control.py` | Veto-Traps für System-Drift und Kausal-Sprünge (Ticket 4). |
| **Arbitration Tests** | `tests/test_arbitration.py` | Veto-Traps für Global Workspace Arbitration (Ticket 5). |
| **Efference Veto Tests** | `tests/test_efference_veto.py` | Verification-First: Veto-Traps für Ticket 6 (Efferenzkopie, Trust-Collapse, Hash). |
| **Temporal Alignment Tests** | `tests/test_temporal_alignment.py` | Verification-First: Veto-Traps für Ticket 7 (Phase 5 & 6, PE, Drehimpulsumkehr). |
| **Audio/Visual Domain Tests (V8)** | `tests/test_audio_visual_domain.py` | Veto-Traps: Zwei-Domänen-Theorie, `tanh`-Projektion, Resonanz-Innenraum, keine AST-Heiler in Kernfunktionen, Embedding/Spreizung. |
| **Ticket 8 Membrane Tests** | `src/scripts/test_ticket_8.py` | Abnahme/Verifikation Dreadnought Membrane (Pain-Flag, Cognitive-Lock, Scanner-Regeln). |
| **Ticket 9 Git-Resonance Tests** | `tests/test_ticket_9.py` | Veto-Traps für Dreadnought Membrane Git-Logik (Auto-Push nach PASS, Pull, Konflikt-Flag). |
| **Ticket 10 OpenClaw Tests** | `tests/test_ticket_10.py` | Veto-Traps: SSH-Heil-Zyklus (`StrictHostKeyChecking=yes`, TrustCollapse), Heartbeat Autonomie-Veto + Pathologie-Log. |
| **OpenClaw VPS Heal** | `src/scripts/heal_openclaw_vps.py` | Ticket 10: SSH-Docker-Restart + Out-of-Band `check_gateway()`. |
| **Ticket 11 Cognitive Membrane** | `docs/05_AUDIT_PLANNING/TICKET_11_COGNITIVE_MEMBRANE.md` | Spec: 4 Säulen (Pre-Flight, O2 Inquisitor, Context Forcing, Apoptose/Timing). |
| **Ticket 11 Masterplan** | `docs/05_AUDIT_PLANNING/MASTERPLAN_TICKET_11_EXECUTION.md` | Umsetzungsplan für Ticket 11. |
| **Ticket 12 Drei Konzepte** | `docs/05_AUDIT_PLANNING/TICKET_12_DREI_KONZEPTE.md` | Architektur-Alternativen für Sentinel & Epistemic Drive (Proaktives Lernen). |
| **Ticket 12 Epistemic Drive** | `docs/05_AUDIT_PLANNING/TICKET_12_EPISTEMIC_DRIVE.md` | Hybride, verbindliche Spezifikation (O2 geprüft): Sentinel, Void Detection, Synthese. |
| **Ticket 11 O2 Audit** | `docs/05_AUDIT_PLANNING/O2_AUDIT_TICKET_11_EXECUTION.md` | Zero-Context Audit von Orchestrator B zu Ticket 11. |
| **O2 Ketten-Kohärenz (Vollkontext)** | `docs/05_AUDIT_PLANNING/O2_AUDIT_KETTEN_KOHAERENZ_2026-04-06.md` | O2 mit Masterplan + Detailfluss + Axiomen: Soll-Kette vs. `run_vollkreis`/Tests; Urteil **[PARTIAL]**; explizite Nicht-Implikationen. |
| **Session-Log 2026-04-01 (Membrane)** | `docs/05_AUDIT_PLANNING/SESSION_LOG_2026-04-01_COGNITIVE_MEMBRANE.md` | Abnahme und Abschluss der Ticket 11 Execution. |
| **Cursor Status (Context Forcing)** | `docs/05_AUDIT_PLANNING/cursor_status.md` | Dynamisch generierter Status-File via Watchdog (Säule 3). |
| **Database** | `src/db/core_infrastructure.sql` | 2D Integer-Membran (SQL-Schema) für CORE-Infrastruktur-Monitoring. |
| **Database** | `src/db/init_infrastructure.py` | Initialisierungs-Skript für die CORE-Infrastruktur-Tabelle auf VPS. |
| **Service** | `src/services/infrastructure_heartbeat.py` | Hintergrund-Service für periodisches Status-Monitoring (Dreadnought, Scout, VPS); Ticket 10: `apply_openclaw_autonomy_veto_if_needed` (Gateway-Down → `/tmp/omega_autonomy_veto.flag` + Pathologie-Log). |
| **Utils** | `src/utils/` | Circuit-Breaker, Zeit-Metriken, Logging-Helfer. |

---

## 3. INFRASTRUKTUR & DEPLOYMENT

### 3.1 Docker-Container
| Container | Pfad | Rolle |
|-----------|------|-------|
| **OpenClaw** | `docker/openclaw-admin/` | Messenger-Gateway (VPS). |
| **Scout** | `docker/scout/` | Edge-Compute-Layer (Pi). |
| **AGI-State** | `docker/agi-state/` | Persistenter Systemzustand. |

### 3.2 Konfiguration
| Datei | Funktion |
|-------|----------|
| `.env` | Zentrale Umgebungsvariablen (Keys, Ports, Hosts). |
| `.cursor/agents/` | Deterministische Sub-Agenten-Rollen (Layer 1). |
| `.cursor/rules/` | Kontextuelle Constraints via MDC-Globs (Layer 2). |
| `.cursorrules` | Primäre operative Direktiven für Agenten. |
| `src/config/core_state.py` | Mathematischer Kern (State Vector, Axiome). |

---

## 4. DATA & MODELS
| Typ | Pfad | Beschreibung |
|-----|------|--------------|
| **ChromaDB** | `data/chroma_db/` | Lokaler Vector-Store (Failover). |
| **WakeWords** | `models/wakeword_mtho/` | Trainierte Modelle für "Hey CORE". |
| **Logdateien** | `logs/` | System- und Audit-Logs. |
| **Legacy-Stempel (Membrane)** | `src/scripts/apply_legacy_stamp.py` | Setzt `[LEGACY_UNAUDITED]` in ältere Markdown-Dateien; verhindert grundlosen Cognitive-Lock (Ticket 8). |

---

## REGEL: INVENTAR-PFLICHT
1. Jede neue Datei (Skript oder Dokument) MUSS unmittelbar in diesem Register nachgetragen werden.
2. Bei Umbenennung oder Löschung ist das Register simultan zu aktualisieren.
3. Der `DOCS_INDEX.md` referenziert dieses Dokument als Master-Liste.
