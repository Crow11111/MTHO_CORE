<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OpenClaw Gateway-Token – Handling und Dokumentation

**Zweck:** Klare Definition, wo und wie der Gateway-Token gespeichert wird, wer ihn nutzt und wie mit Rotation/Expiry umgegangen wird.

---

## 1. Definition

- **OPENCLAW_GATEWAY_TOKEN:** Ein geheimer Token, mit dem sich CORE (und ggf. andere berechtigte Dienste) beim OpenClaw-Gateway authentifizieren (z. B. für Kanal-Kommunikation, Status, Senden von Nachrichten).
- Der Token wird **nur** in der Admin-OpenClaw-Instanz und in den Instanzen, die mit dem Gateway sprechen (CORE), benötigt. Spine- und weitere Executor-Instanzen können einen eigenen oder denselben Token nutzen – je nach Architektur (siehe [OPENCLAW_ADMIN_ARCHITEKTUR.md](OPENCLAW_ADMIN_ARCHITEKTUR.md)).

---

## 2. Speicherort

| Ort | Inhalt | Zugriff |
|-----|--------|--------|
| **CORE** | `.env` (lokal, nicht versioniert): `OPENCLAW_GATEWAY_TOKEN=...` | Nur auf 4D_RESONATOR (CORE)/Entwicklungsrechner; wird von Skripten und API (z. B. `openclaw_client.py`) gelesen. |
| **OpenClaw-Admin-Container** | Umgebungsvariable `OPENCLAW_GATEWAY_TOKEN` (via Docker Compose / Deploy-Skript aus CORE .env gesetzt) oder in `openclaw.json` unter `gateway.auth.token` | Nur innerhalb des Containers; nicht in Repo committen. |
| **Spine / weitere Instanzen** | Wenn sie direkt mit dem Gateway reden: Token aus eigener Konfiguration oder zentral (z. B. über Admin) – je nach Architektur. | Dokumentiert in OPENCLAW_ADMIN_ARCHITEKTUR.md. |

- **Keine** Token in Git, keine Klartext-Token in öffentlichen Repos oder Logs.

---

## 3. Verwendung

- **CORE:** `src/network/openclaw_client.py` – liest `OPENCLAW_GATEWAY_TOKEN` aus der Umgebung (geladen aus `.env`); sendet Token bei HTTP-Anfragen an das Gateway (Header oder Query, je nach OpenClaw-API).
- **OpenClaw-Gateway:** Erwartet den Token bei eingehenden Anfragen; ohne gültigen Token werden Anfragen abgewiesen (401/403).
- **Port/Host:** `OPENCLAW_GATEWAY_PORT` (z. B. 18789 oder 58105 bei Hostinger) und Host (VPS_HOST oder OPENCLAW_ADMIN_VPS_HOST) in CORE .env; siehe [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](../03_INFRASTRUCTURE/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md).

---

## 4. Rotation und Ablauf

- **Rotation:** Noch nicht automatisiert. Manuell: Neuen Token erzeugen (OpenClaw/Admin-UI oder Konfiguration), in CORE `.env` und in der Admin-OpenClaw-Config eintragen, Dienste neu starten.
- **Expiry:** Aktuell kein Ablauf definiert; Token bleibt gültig bis zur manuellen Änderung. Wenn OpenClaw später Expiry unterstützt, hier und in der Betriebsdoku ergänzen.

---

## 5. Checkliste (Betrieb)

- [ ] Token nur in `.env` und in Container-ENV, nicht in Code oder Repo.
- [ ] Nach Token-Wechsel: `.env` aktualisieren, OpenClaw-Admin-Config/ENV aktualisieren, betroffene Container/Dienste neu starten.
- [ ] Zugriff auf `.env` und VPS-Config nur für berechtigte Personen; SSH und Secrets siehe [PROJEKT_ANNAHMEN_UND_KORREKTUREN.md](../05_AUDIT_PLANNING/PROJEKT_ANNAHMEN_UND_KORREKTUREN.md) (Abschnitt SSH und Secrets).
