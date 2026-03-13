<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Wiedervorlage: WhatsApp Pairing + CORE-Weiterbau

**Angelegt:** 28.02.2026  

---

## CORE-Pipeline (ohne Warten auf WhatsApp)

- **Scout → OMEGA_ATTRACTOR:** `send_event_to_oc_brain(event)` / `python -m src.scripts.scout_send_event_to_oc` (stdin JSON oder --type/--node/--device).
- **Event-Ingest API:** `POST /api/core/event` – Body: source, node_id, event_type, priority, data → speichert in `data/events/` + ChromaDB `events`.
- **OMEGA_ATTRACTOR SOUL:** Event-Protokoll im Deploy (Eingabe = Scout-JSON → bestätigen, Logik laut ARCHITECTURE.md).
- **ChromaDB:** Collections `events`, `insights` in chroma_client; Events werden mit Metadata gespeichert.

WhatsApp später pairen, wenn Slot/Throttle es erlauben.

---

## 1. Bei Gelegenheit (WhatsApp)

- **WhatsApp erneut pairen:** Control-UI → Channels → WhatsApp. Slot ist frei (3/4 belegt).

---

## 2. CORE funktional weiterbauen

Ziel = **funktionales Tool** wie in CORE Neocortex V1.0 und Schnittstellen-Doc beschrieben:

- **Scout → OMEGA_ATTRACTOR:** Webhook POST `/v1/responses` mit Event-JSON (source, node_id, event_type, data).
- **OMEGA_ATTRACTOR:** Logik (4D_RESONATOR (CORE)-Status), ChromaDB/State, Eskalation per WhatsApp (`[CORE-ALERT]`).
- **Kanäle:** 4D_RESONATOR (CORE)↔OC (bereits), rat_submissions (bereits), WhatsApp (nach Pairing), Scout-Webhook (Endpoint steht; Scout-Seite anbinden).

Konkret nach dem Pairing:

1. WhatsApp-Pairing verifizieren (Testnachricht an OC, Antwort prüfen).
2. Scout so konfigurieren, dass er bei relevanten Events POST an OMEGA_ATTRACTOR sendet (Payload laut CORE_SCHNITTSTELLEN_UND_KANAALE.md).
3. Optional: ChromaDB-Collections `events`/`insights` auf VPS anlegen und in die Pipeline einhängen.

Referenz: `docs/02_ARCHITECTURE/CORE_AGI_ARCHITECTURE.md`, `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md`.
