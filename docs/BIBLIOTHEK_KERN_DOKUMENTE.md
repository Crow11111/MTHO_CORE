# ATLAS_CORE Bibliothek – Kerndokumente & Index

Dieses Dokument dient als Einstiegspunkt ("Bibliothek") für neue Chat-Sessions oder Agenten-Tasks. Es gruppiert die zahlreichen Projektdateien in logische Kategorien, sodass man sofort weiß, welche Dateien als Kontext (`@`) übergeben werden müssen.

---

## 1. Die "Big 3" Kern-Dokumente (Allgemeine Architektur & Schnittstellen)
*Diese drei Dateien geben den besten Gesamtüberblick über das Setup. Wenn du unsicher bist, starte hiermit.*

- **`@docs/DEV_AGENT_UND_SCHNITTSTELLEN.md`**
  Das Herzstück: Wer ruft wen wie auf. Beinhaltet LLM-Zuordnungen, Backup-Pläne, API-Strukturen und Netzwerk-Verweise.
- **`@docs/OPENCLAW_ADMIN_ARCHITEKTUR.md`**
  Die Architektur-Logik für OpenClaw (OC) auf dem VPS: Aufteilung in **Brain/Admin** (mit Provider-Keys) und **Spine** (als Slave ohne Keys).
- **`@docs/VPS_FULL_STACK_SETUP.md`**
  Das physische Setup auf Hostinger: Container (Home Assistant, OpenClaw Admin/Spine, ChromaDB), Netzwerke, Ports und Firewall-Regeln.

---

## 2. Themen-Spezifische Dokumente

### 2.1 WhatsApp & Home Assistant
*Wenn es um eingehende/ausgehende WhatsApp-Nachrichten über die lokale HA-Instanz geht.*

- **`@docs/WHATSAPP_E2E_HA_SETUP.md`**
  Der private Scout/HA-Pfad (Addon -> Event -> rest_command -> ATLAS API -> send_whatsapp).
- **`@docs/WHATSAPP_ROUTING_ATLAS_OC.md`**
  Die Logik: Wann reagiert `@Atlas`, wann `@OC`.

### 2.2 VPS / Hostinger (OpenClaw Betrieb)
*Wenn der Agent Tasks auf dem VPS ausführen soll (Container warten, Logs prüfen).*

- **`@docs/VPS_FULL_STACK_SETUP.md`**
  Siehe oben (Ports, IPs, Deploy-Skript `deploy_vps_full_stack.py`).
- **`@docs/exchange/OC_ATLAS_SESSION_ABSCHLUSS.md`**
  Protokoll und Status der letzten Interaktionen mit OpenClaw auf dem VPS.

### 2.3 Grundlegende Haltung / Rolle / Audio
*Für Prompt-Design, Tonalität, Voice-Ausgabe und Agenten-Grenzen.*

- **`@docs/stammdokumente_oc/03_OC_ROLLE_UND_GRENZEN.md`**
  Deine Regeln, Sandboxing und die Abgrenzung zwischen OC und ATLAS.
- **`@docs/ATLAS_VOICE_ARCHITECTURE_V1.3.md`**
  Audio-Architektur, ElevenLabs-Integration und Voice-States.

---

## 3. Austausch und Abstimmung (Exchange)
Für laufende Abstimmungen, Handshakes, Rückfragen und Status-Updates zwischen dem ATLAS-Team und Agenten (z.B. OC) existiert das Verzeichnis:

- **`docs/exchange/`**
  (Hier werden keine statischen Architektur-Regeln abgelegt, sondern fortlaufende Briefings und Reports).

---

## 4. Offene Punkte / Backlog
- **`@docs/OFFENE_PUNKTE_AUDIT.md`**
  Liste technischer Schulden (Token-Überwachung, Vaultwarden, HTTPS/Webhook-Sicherheit).