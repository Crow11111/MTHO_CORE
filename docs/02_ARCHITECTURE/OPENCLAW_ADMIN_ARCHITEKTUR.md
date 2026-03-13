<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OpenClaw-Architektur: Admin (Gehirn) vs Spine (Rückenmark)

**Stand:** Nach Einführung der nativen OpenClaw-Admin-Instanz. Zwei (später drei) OpenClaw-Instanzen im CORE-Ökosystem.

---

## 1. Rollen

| Instanz | Rolle | API-Keys / Zugriff | Aufgabe |
|--------|--------|---------------------|--------|
| **OpenClaw Admin** | Gehirn (Boss) | Alle Keys: GEMINI_API_KEY, ANTHROPIC_API_KEY, NEXOS_API_KEY (Guthaben), WhatsApp, Gateway-Token. Vollzugriff. | Einzige Instanz mit direkter Verbindung zu Google/Anthropic/Nexos/Messenger. Steuert und verwaltet; kann überall eingreifen (HA, CORE, Spine). |
| **OpenClaw Spine** | Rückenmark (ausführend) | Keine direkten Provider-Keys für Google/Anthropic. Nur Gateway-Token für Kommunikation mit Admin. | Organisiert Daten, führt aus; für Google/Konto-Zugriffe etc. wendet er sich an die Admin-Instanz. |
| **OpenClaw (dritte Instanz, geplant)** | Zusätzlicher Executor | Wie Spine: keine sensiblen Keys, Kommunikation über Admin. | Später; Daten der bisherigen Instanz werden in die neue überführt. |

**Prinzip:** Nur die **Admin-Instanz** stellt die wirkliche Verbindung zu externen Diensten (Google, Anthropic, WhatsApp, ggf. HA) her. Die anderen Instanzen (Spine, künftig dritte) sind ausführende Knoten und holen sich Berechtigungen/Proxying über den Admin.

---

## 2. Sicherheitskonzept

- **Admin** = Single Point mit allen ENV-Keys und Gateway-Token. Wird über **eigene Docker-Compose-Instanz** (nativ, nicht Hostinger-managed) betrieben, damit Config (z. B. Google Provider, gemini-3.1-pro-preview) voll kontrollierbar ist.
- **Spine** = Bestehende Hostinger-Instanz (oder spätere Executor-Instanz). Erhält **keine** GEMINI/ANTHROPIC-Keys in der Umgebung; Kommunikation mit dem Ökosystem (CORE, HA) läuft über den Admin oder über definierte Tokens (z. B. OPENCLAW_GATEWAY_TOKEN nur für Kanal, nicht für Provider).
- **SSH:** Vollständiger SSH-Zugang nur für die Admin-VPS-Instanz (bzw. die VPS, auf der der Admin-Container läuft). Spine-VPS kann separat verwaltet werden; Admin-VPS ist die zentrale Steuerungsstelle.

---

## 3. Einbindung ins CORE-Ökosystem

- Die **neue Admin-Instanz** ist genauso eingebunden wie bisher die OpenClaw-Instanz: gleicher Gateway-Token (oder eigener Admin-Token), WhatsApp (allowFrom aus WHATSAPP_TARGET_ID), gleiche Kanäle (WhatsApp, optional Telegram).
- CORE (4D_RESONATOR (CORE)) spricht mit dem **Admin**-Gateway (OPENCLAW_GATEWAY_TOKEN, OPENCLAW_ADMIN_VPS_HOST / OPENCLAW_GATEWAY_PORT). Home Assistant und andere Komponenten, die OpenClaw ansprechen, zeigen auf den Admin.
- Die bisherige (Spine-)Instanz kann für spezifische Aufgaben weiterlaufen; sie greift für LLM/API auf den Admin zu oder wird schrittweise auf die dritte Instanz umgestellt und dann repariert/konfiguriert.

---

## 4. Vorgaben für die Admin-Instanz

- **Modelle:** Nur 3.x/Pro-Modelle, kein 2.0 Flash. Primär **Gemini 3.1 Pro** (gemini-3.1-pro-preview), Fallback **Gemini 3.0 Preview** (gemini-3-pro-preview); **Claude Opus 4.6** und **Claude Sonnet 4.6** (Anthropic); **Nexos** (eigener Zugang, Guthaben) – alles unter unserer Kontrolle. Verbindliche Annahmen: [PROJEKT_ANNAHMEN_UND_KORREKTUREN.md](../05_AUDIT_PLANNING/PROJEKT_ANNAHMEN_UND_KORREKTUREN.md).
- **WhatsApp:** eingerichtet (allowFrom aus .env WHATSAPP_TARGET_ID).
- **ENV:** Alle für OpenClaw benötigten Keys aus der CORE .env: GEMINI_API_KEY, ANTHROPIC_API_KEY, NEXOS_API_KEY (optional), OPENCLAW_GATEWAY_TOKEN, WHATSAPP_TARGET_ID; VPS-Zugang (SSH) für die Admin-VPS.
- **Deployment:** Native Docker-Compose-Installation (nicht Hostinger-App-Catalog), damit Google-Provider und Modellauswahl uneingeschränkt konfigurierbar sind.

---

## 5. Referenzen

- **Deployment:** [Deploy-Skript](../../src/scripts/deploy_openclaw_admin_vps.py), [Docker-Compose](../../docker/openclaw-admin/).
- **Gateway-Token:** [OPENCLAW_GATEWAY_TOKEN.md](OPENCLAW_GATEWAY_TOKEN.md).
- **Nexos:** [NEXOS_EINBINDUNG.md](NEXOS_EINBINDUNG.md) (Daten von bestehender OpenClaw-Instanz).
- **VPS & Sandbox:** [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](../03_INFRASTRUCTURE/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md).
- **Projekt-Annahmen:** [PROJEKT_ANNAHMEN_UND_KORREKTUREN.md](../05_AUDIT_PLANNING/PROJEKT_ANNAHMEN_UND_KORREKTUREN.md).
