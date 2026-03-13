<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Scout (HA auf Raspi): Event an OMEGA_ATTRACTOR senden

Damit der Scout nach Neustart oder bei Sensor-/Kamera-Trigger ein Event an OMEGA_ATTRACTOR schickt, muss HA den VPS-Endpunkt aufrufen.

---

## Copy-Paste (komplett)

**1. Geheimnisse** (Einstellungen → Geheimnisse oder `secrets.yaml`):
- `oc_brain_url`: `https://187.77.68.250` oder `http://187.77.68.250:18789`
- `oc_brain_token`: aus CORE `.env` → `OPENCLAW_GATEWAY_TOKEN`

**2. configuration.yaml** (oder YAML-Add-on):

```yaml
rest_command:
  scout_online_to_oc:
    url: "{{ oc_brain_url }}/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer {{ oc_brain_token }}"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: '{"model":"openclaw","input":"{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"scout_online\",\"priority\":\"low\",\"data\":{}}}"}'

automation:
  - alias: "Scout online → OMEGA_ATTRACTOR"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - delay: "00:01:00"
      - service: rest_command.scout_online_to_oc
```

`oc_brain_url` ohne Port (z. B. `https://187.77.68.250`) → Pfad `/v1/responses` wird angehängt. Mit Port (`http://187.77.68.250:18789`) ebenso.

---

## 1. Token und URL in HA

In **Einstellungen → Geräte & Dienste → Geheimnisse** (oder `secrets.yaml`):

```yaml
oc_brain_url: "http://187.77.68.250:18789"
oc_brain_token: "DEIN_OPENCLAW_GATEWAY_TOKEN"
```

(Bei Nginx-HTTPS: `oc_brain_url: "https://187.77.68.250"` und Port weglassen.)

---

## 2. rest_command in HA

In `configuration.yaml` oder als YAML-Konfiguration:

```yaml
rest_command:
  scout_event_to_oc_brain:
    url: "{{ oc_brain_url }}/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer {{ oc_brain_token }}"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: >
      {
        "model": "openclaw",
        "input": "{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"{{ event_type }}\",\"timestamp\":\"{{ now().isoformat() }}\",\"priority\":\"{{ priority | default('medium') }}\",\"data\":{{ data | default('{}') | tojson }}}"
      }
```

**Hinweis:** `event_type`, `priority`, `data` müssen bei Aufruf übergeben werden (siehe Automation).

---

## 3. Einfacher Aufruf (festes Event)

In `configuration.yaml` (oder YAML-Add-on):

```yaml
rest_command:
  scout_online_to_oc:
    url: "http://187.77.68.250:18789/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer DEIN_OPENCLAW_GATEWAY_TOKEN"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: '{"model":"openclaw","input":"{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"scout_online\",\"priority\":\"low\",\"data\":{}}}"}'
```

Token und URL besser in `secrets.yaml`: `oc_brain_url`, `oc_brain_token` – dann `url: !secret oc_brain_url` und `Authorization: "Bearer " + secrets["oc_brain_token"]` (in HA oft als Template).

---

## 4. Automation: Nach Neustart oder manuell

- **Trigger:** Start von Home Assistant (Event `homeassistant_start`) oder ein manueller Schalter.
- **Aktion:** `rest_command.scout_online_to_oc` (oder `scout_event_to_oc_brain` mit Parametern).

Beispiel (Start-Event):

```yaml
automation:
  - alias: "Scout online → OMEGA_ATTRACTOR"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - delay: "00:01:00"
      - service: rest_command.scout_online_to_oc
```

---

## 5. Von 4D_RESONATOR (CORE) aus testen (ohne HA)

```bash
python -m src.scripts.scout_send_event_to_oc --type scout_online --node raspi5-ha-master
```

Damit wird das Event von deinem PC an OMEGA_ATTRACTOR gesendet (gleicher Kanal wie vom Scout).
