# ATLAS_CORE – Dokumentationsindex

Zentrale Übersicht: Welche Doku gibt es, wo steht was, wie hängt es zusammen.

---

## 1. Stammdokumente (für OC)

**Zweck:** Für **OC (OpenClaw)** einsehbar – erklärt das Projekt, Marc, das Team und OCs Rolle/Grenzen.

- **Ordner:** [docs/stammdokumente_oc/](stammdokumente_oc/00_INDEX.md)
- **Inhalt:** 00_INDEX, 01_PROJEKT_ATLAS, 02_MARC_UND_TEAM, 03_OC_ROLLE_UND_GRENZEN
- **Ablage auf Hostinger:** Nach Freigabe durch den Rat werden die Stammdokumente auf dem VPS unter dem OC-Workspace bereitgestellt; Marc informiert OC per WhatsApp. Siehe [STAMMDOKUMENTE_DEPLOY.md](STAMMDOKUMENTE_DEPLOY.md).

---

## 2. Architektur & Schnittstellen

| Dokument | Inhalt |
|----------|--------|
| [DEV_AGENT_UND_SCHNITTSTELLEN.md](DEV_AGENT_UND_SCHNITTSTELLEN.md) | Dev-Agent, Backup, **Netzarchitektur Messenger & OC**, WhatsApp/HA, VPS-Setup |
| [WHATSAPP_OPENCLAW_VS_HA.md](WHATSAPP_OPENCLAW_VS_HA.md) | OC vs. HA-Pfad, getrennte Kanäle, wie man welchen Kanal erreicht |
| [WHATSAPP_E2E_HA_SETUP.md](WHATSAPP_E2E_HA_SETUP.md) | E2E-Setup (rest_command, Automation), **Präfix [ATLAS]/[Scout]** |
| [KANAL_ATLAS_OC.md](KANAL_ATLAS_OC.md) | **Direkter Kanal ATLAS ↔ OC** (Nachrichten an Agent, Rat-Einreichungen OC → ATLAS) |
| [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md) | Dienste auf Hostinger, OC-Sandbox-Pflicht |

---

## 3. Umsetzung & Tasks

| Dokument | Inhalt |
|----------|--------|
| [UMSETZUNGSPLANUNG.md](UMSETZUNGSPLANUNG.md) | Konkrete Tasks (Backup, WhatsApp, OC-Kanäle, Status-Anzeige, offene Punkte) |
| [OFFENE_PUNKTE_AUDIT.md](OFFENE_PUNKTE_AUDIT.md) | Offene Punkte aus Dev-Agent-Audit (HMAC, TLS, Vaultwarden, …) |

---

## 4. Backup & Sicherheit

| Dokument | Inhalt |
|----------|--------|
| [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md) | Einziges Ziel: Hostinger-VPS, Skript daily_backup.py, Retention |

---

## 5. Dev-Agent & Review

| Dokument | Inhalt |
|----------|--------|
| [dev_agent_review_context.md](dev_agent_review_context.md) | Kontext für Review (Schnittstellen, Architektur, Sicherheit) |
| [DEV_AGENT_PARALLEL.md](DEV_AGENT_PARALLEL.md) | Parallelisierung (APIs, Sub-Tasks) |
| [DEV_AGENT_TESTS_SPEC.md](DEV_AGENT_TESTS_SPEC.md) | Tests (Kamera, WhatsApp, OC) |
| [CREW_MANIFEST.md](CREW_MANIFEST.md) | Rollen (Architect Zero, Backend Forge, Net Engineer, UI Artist) |

---

## 6. Weitere (Kamera, Voice, ND, …)

- [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md), [ATLAS_VOICE_ARCHITECTURE_V1.3.md](ATLAS_VOICE_ARCHITECTURE_V1.3.md)
- nd_insights, BACKUP_PLAN (Vorläufer) – je nach Bedarf

---

**Konsolidierung:** Neue Themen (z. B. OC, Stammdokumente, Präfix) sind in die bestehenden Docs eingepflegt; dieser Index verweist darauf. Stammdokumente für OC liegen unter `docs/stammdokumente_oc/` und werden nach Rat-Freigabe auf den Server deployed.
