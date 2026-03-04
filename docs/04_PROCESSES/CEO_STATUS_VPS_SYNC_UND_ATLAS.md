# CEO-Status: VPS-Sync & ATLAS-Aufbau

**Stand:** 2026-03. **Orchestrator:** Budget gesetzt, VPS-Sync vorbereitet, nächste Schritte festgelegt.

---

## 1. Budget (Token)

- **Phase 1 (VPS/Abgleich):** ~2.000–4.000 Token (laut CEO-Plan).
- **Gesamt-Roadmap:** Siehe `docs/05_AUDIT_PLANNING/CEO_PLAN_OC_BRAIN_ABGLEICH_UND_ROLLOUT.md`.
- **Schwellen:** Unter 5.000 Reserve → nur 1 Team, max. 200 Token/Call. Unter 3.000 → STOP, Workaround dokumentieren.

---

## 2. VPS-Sync – aktueller Stand

| Punkt | Status |
|-------|--------|
| Ping/Port 22 zum VPS | OK (vom User-Rechner aus). |
| Paramiko-SSH (Skript) | Verbindung zum VPS gelingt. |
| Tunnel-Kanal (VPS 127.0.0.1:8000) | **Connection refused** – auf dem VPS antwortet kein Dienst auf Port 8000. |
| Lokaler Tunnel-Port | 8001 (Konflikt mit Backend 8000 vermieden). |
| Fallback | System-SSH (Key-Auth) eingebaut; Paramiko läuft zuerst. |

**Ursache der Blockade:** ChromaDB (oder der Container, der Port 8000 exponiert) auf dem VPS läuft nicht oder lauscht nicht auf 127.0.0.1:8000.

**Nächster Schritt (User/VPS):** Auf dem VPS prüfen, ob ChromaDB/Container laufen und Port 8000 gebunden ist. Danach Sync erneut ausführen:

```powershell
cd C:\ATLAS_CORE
python -m src.scripts.run_vps_sync_with_tunnel
```

**Manueller Weg (wenn automatisch weiter fehlschlägt):** In einem Fenster Tunnel starten (`ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N`), in einem zweiten Fenster Sync + Abgleich mit Port 8001 (siehe `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md`).

---

## 3. ATLAS-Aufbau – nächste Meilensteine (CEO)

1. **Ring-0/VPS-Sync:** Sobald VPS-Chroma auf 8000 antwortet → Sync + Abgleich ausführen, Vergleichsdokument Abschnitt 2 ausfüllen.
2. **Cursor/Regeln:** Reduktion und fraktale Verteilung (laut CURSOR_ATLAS_SPEC) – bereits angestoßen; bei Bedarf Team A (Cursor/DB/API) nachziehen.
3. **DB-Migration:** Gravitations-Logik (Migrationsreihenfolge Judge-bestätigt) – Ring-0-Sync zuerst, dann Cursor-Reduktion, dann Query-Code.
4. **Dissonanz-Schwellwerte:** Spec mit bewerteter Fassung (User Vorschlag C) steht; Implementierung in Shadow-Mode mit Auswertung „morgen nach 12 Uhr“.
5. **Tool-Audit, Chat Team B, Zusammenfassung, OC-Brain-Fix:** Gemäß CEO-Plan nacheinander abarbeiten; Budget und Token-Druck je Phase anpassen.

---

## 4. Nächste Aktion (Tokendruck aufrechterhalten)

- **Sofort (ohne User):** Cursor/Regeln – Reduktion 1–4.mdc erledigt (keine Tetralogie-Kopie; Verweis auf .cursorrules). User-Entlastung in .cursorrules ergänzt.
- **Sobald VPS-Chroma läuft:** `python -m src.scripts.run_vps_sync_with_tunnel` → Abgleich in VERGLEICHSDOKUMENT eintragen.
- **Danach:** DB-Migration Query-Code (gravitationskonform); Dissonanz Shadow-Mode (Spec steht); dann Tool-Audit / Team B / Zusammenfassung.

---

## 5. Referenzen

- **VPS-Sync:** `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md`
- **Vergleichsdokument:** `docs/05_AUDIT_PLANNING/VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md`
- **CEO-Plan (Phasen/Budget):** `docs/05_AUDIT_PLANNING/CEO_PLAN_OC_BRAIN_ABGLEICH_UND_ROLLOUT.md`
- **Kern-Kontext:** `docs/05_AUDIT_PLANNING/ATLAS_KERN_CONTEXT.md`
- **Bibliothek Kerndokumente:** `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`
