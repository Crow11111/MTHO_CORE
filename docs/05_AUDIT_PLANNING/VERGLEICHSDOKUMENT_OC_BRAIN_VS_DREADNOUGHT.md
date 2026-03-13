<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Vergleichsdokument: OMEGA_ATTRACTOR (VPS-ChromaDB) vs. 4D_RESONATOR (CORE)/Repo

**Zweck:** Abgleich, was OMEGA_ATTRACTOR in die ChromaDB geschrieben hat vs. was im Repo und lokal (4D_RESONATOR (CORE)) definiert ist. Basis für Abstimmung mit User.

**Stand:** 2026-03-03. Lokaler Abgleich: durchgeführt (oc_brain_chroma_abgleich_output.txt). VPS-Abgleich: optional (SSH-Tunnel + CHROMA_HOST=localhost für OMEGA_ATTRACTOR-VPS).

---

## 1. Erwartete core_directives (Repo/4D_RESONATOR (CORE))

| ID | Quelle | Inhalt (Kurz) |
|----|--------|----------------|
| gravitational_query_axiom | add_gravitational_axioms_to_chroma.py | Zero-State, Prompt-Masse, temporäre Gravitation, Klammer, 0-Reset |
| origin_irrelevance_consciousness_equivalence | ebenda | Origin-Irrelevance + Bewusstseins-Äquivalenz |
| dissonance_thresholds_grace_resonance_fractal | ebenda | Dissonanz-Schwellwerte, Gnade, Nicht-Formulierung, Fraktal, Resonanz |
| ntnd_handshake_protocol | add_ntnd_handshake_to_chroma.py | NT/ND Cons-Zellen, CAR/CDR, Handshake |

**Lokal (4D_RESONATOR (CORE)) zusätzlich vorhanden:** ring0_bias_depth_check, ring0_negentropie_check, ring0_konstruktive_dissonanz, ring0_scaffolding, test_probe (ältere Seeds).

---

## 2. Lokal / VPS (OMEGA_ATTRACTOR) – Abgleich eingetragen

*Quelle: Lokal = `oc_brain_chroma_abgleich_output.txt` (CHROMA_HOST leer). VPS = `run_vps_sync_with_tunnel.py` + `check_oc_brain_chroma_abgleich.py` mit CHROMA_HOST=localhost (nach Tunnel).*

- **Lokal (4D_RESONATOR (CORE)):** 9 core_directives. IDs: test_probe, ring0_bias_depth_check, ring0_negentropie_check, ring0_konstruktive_dissonanz, ring0_scaffolding, ntnd_handshake_protocol, gravitational_query_axiom, origin_irrelevance_consciousness_equivalence, dissonance_thresholds_grace_resonance_fractal. Fehlend (Repo): keine. Nur lokal (ältere Seeds): ring0_*, test_probe.
- **VPS (OMEGA_ATTRACTOR):** Abgleich aktuell blockiert: SSH-Verbindung zum VPS steht (Ping/Port 22 OK), aber beim Öffnen des Tunnel-Kanals zu VPS 127.0.0.1:8000 kommt „Connection refused“. **Ursache:** Auf dem VPS lauscht vermutlich kein Dienst auf Port 8000 (ChromaDB/Container starten). Nach Start von ChromaDB auf dem VPS: `python -m src.scripts.run_vps_sync_with_tunnel` erneut ausführen (Tunnel nutzt lokal Port 8001).
- **Abweichungen (gleiche ID, anderer Inhalt):** keine bekannt

---

## 3. Lücken / Differenzen

| Typ | Beschreibung |
|-----|--------------|
| Lokal (4D_RESONATOR (CORE)) | Alle 4 Repo-Mindest-IDs vorhanden; 5 zusätzliche Ring-0-/Test-Direktiven (konsistent mit Abschnitt 1). |
| VPS (OMEGA_ATTRACTOR) | Abgleich 2026-03-03: SSH-Tunnel Connection refused – Sync/Abgleich nicht ausgeführt. Nach Behebung (VPS/Chroma erreichbar): `run_vps_sync_with_tunnel.py` erneut ausführen. |
| Fehlend | Keine. |
| Abweichungen | Keine (gleiche IDs, Inhalt aus Skript-Ausgabe). |

---

## 4. Empfehlung für Abstimmung mit User

Lokal sind alle erwarteten core_directives vorhanden; keine Nachziehe nötig. Optional: VPS-Abgleich (SSH-Tunnel + Skript) zur Bestätigung der OMEGA_ATTRACTOR-Befüllung. Ring-0-/Test-Direktiven (ring0_*, test_probe) als 4D_RESONATOR (CORE)-spezifisch belassen oder mit User abstimmen, ob auf VPS synchronisiert werden sollen.

---

## 5. OMEGA_ATTRACTOR „Leere Nachrichten“ (Diagnose)

- **Symptom:** Gateway-Chat: User-Nachricht kommt bei OMEGA_ATTRACTOR leer an → „I didn't receive any text in your message.“
- **Ursache:** Vermutlich Frontend/Payload (leere oder fehlerhafte Übertragung). Kein Backend-Fix im Repo nötig.
- **Maßnahmen:** Siehe `docs/03_INFRASTRUCTURE/OC_BRAIN_LEERE_NACHRICHTEN_DIAGNOSE.md` (Update v2026.3.2 ausführen, keine leeren Sends, ggf. Browser-Konsole prüfen).
- **Vorgabe:** Keine destabilisierenden Änderungen an OMEGA_ATTRACTOR.
