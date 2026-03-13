<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# OpenClaw Brain: Config validieren, andere Modelle als Gemini 2.5

Kurz: **GatewayRequestError: invalid config** = Schema-Validierung schlägt fehl. **Brain nutzt nur Gemini 2.5** = oft Folge davon oder Modell-Liste/Agent-Modell falsch.

---

## 1. Exakte Fehlerstelle ermitteln: `openclaw doctor`

**Von 4D_RESONATOR (CORE) aus (mit .env für VPS):**

```bash
python -m src.scripts.openclaw_doctor_vps
```

**Oder direkt auf dem VPS** (per SSH):

```bash
docker ps --format '{{.Names}}' | grep -i openclaw
docker exec <CONTAINER> openclaw doctor
```

Alternativ Logs ansehen:

```bash
docker logs <CONTAINER> 2>&1 | tail -100
# oder falls mit pm2: pm2 logs openclaw
```

`openclaw doctor` gibt den **genauen Pfad** des Schema-Verstoßes aus – nicht raten.

---

## 2. Zwei typische Ursachen für „invalid config“

### A) Platzhalter in Auth-Feldern (kritisch)

Config enthält z. B.:

- `"apiKey": "__OPENCLAW_REDACTED__"`
- `"token": "__OPENCLAW_REDACTED__"`
- `"apiKey": "$ANTHROPIC_API_KEY"` (wenn der Gateway **keine** Env-Substitution macht)

**Lösung:** Beim Deploy **niemals** REDACTED oder reine Env-Variablennamen schreiben. Stattdessen:

- API-Keys und Tokens aus der lokalen `.env` lesen.
- Beim Schreiben der Config auf den VPS die echten Werte einsetzen (z. B. über `deploy_openclaw_config_vps.py` mit Env-Injection).

Dann prüfen: Nach Deploy enthält `openclaw.json` auf dem Host/Container **echte** Werte (Länge/Format plausibel), keine Platzhalter.

### B) Struktur (Schema): `workspace`, `list`, `model.primary`, `defaults.models`

Laut OpenClaw-Schema (config.clawi.sh, v2026.2.x):

- `agents.defaults.workspace` = Default-Workspace-Pfad (z. B. `/home/node/.openclaw/workspace`).
- `agents.list` = Array der Agenten-Definitionen (jeweils `id`, `name`, `model`).
- **`agents.defaults.model.primary`** = **Modell-ID** im Format `provider/model-id` (z. B. `google/gemini-2.5-pro`), **nicht** der Anzeigename (Alias). Ein Alias hier führt zu Schema-/UI-Fehlern.
- **`agents.defaults.models`** = Record: Key = `provider/model-id`, Value = `{ "alias": "Anzeigename" }`. Alle in der UI wählbaren Modelle müssen hier mit Alias eingetragen sein; zusätzlich unter `models.providers.<provider>.models` als Array von `{ "id", "name" }`.
- **`models.providers.<provider>.models`** = Array von Objekten `{ "id": "model-id", "name": "Anzeigename" }` (ohne Provider-Präfix im `id`).

Beides `workspace` und `list` gehört **unter** `agents` (nicht auf Root-Ebene). Mit `openclaw doctor` siehst du den exakten Pfad bei Schema-Verstößen.

---

## 3. Andere Modelle (nicht nur Gemini 2.5)

Damit das Brain **andere Modelle** (z. B. Claude, Nexos, weitere Gemini-Varianten) nutzen kann:

1. **Provider mit echten Keys:**  
   In der Config müssen `models.providers.*.apiKey` (und ggf. `token`) **gültige** Werte haben. Bei Platzhaltern schlägt oft schon die Initialisierung fehl, dann bleibt nur Fallback (z. B. Gemini 2.5).

2. **Modell-Liste pro Provider:**  
   Unter `models.providers.<provider>.models` die gewünschten Modelle eintragen (z. B. `gemini-2.5-pro`, `claude-sonnet-4-5`, Nexos-IDs).

3. **Agent-Modell:**  
   `agents.list[].model` und `agents.defaults.model.primary` **müssen** die Modell-ID im Format `provider/model-id` sein (z. B. `google/gemini-2.5-pro`), **nicht** der Alias. Sonst Schema-Fehler / nur ein Modell in der UI.

4. **Defaults / Aliase:**  
   Unter `agents.defaults.models` für **jedes** genutzte Modell einen Eintrag: Key = `provider/model-id`, Value = `{ "alias": "Anzeigename" }`. Ohne diese Einträge erscheinen nicht alle Modelle in der UI.

Nach Änderungen: Config ohne REDACTED/$VAR auf den VPS deployen, Container neustarten, dann erneut `openclaw doctor` und einen Test-Request (z. B. über CORE) ausführen.

---

## 4. Empfohlener Ablauf

1. Lokal: `.env` mit gültigen Werten für `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENCLAW_GATEWAY_TOKEN`.
2. Deploy so ausführen, dass **nur echte Werte** aus der `.env` in die Config geschrieben werden (z. B. `python -m src.scripts.deploy_openclaw_config_vps` mit Env-Injection).
3. Auf dem VPS: `docker exec <CONTAINER> openclaw doctor` → Fehlerpfad beheben.
4. Container neustarten; danach Brain mit anderem Modell testen (z. B. Agent auf `anthropic/claude-sonnet-4-5` stellen).

**Deploy mit Env-Injection (keine Platzhalter auf den VPS):**  
`python -m src.scripts.deploy_openclaw_config_vps` ersetzt in der gelesenen Config alle Vorkommen von `__OPENCLAW_REDACTED__` und `$VAR` in `apiKey`/`token` durch Werte aus der lokalen `.env`, setzt `agents.defaults.model.primary` auf Modell-ID (nicht Alias), füllt `agents.defaults.models` für alle Google- und Anthropic-Modelle (UI-Auswahl), entfernt `imageModel`-Keys (Schema) und schreibt `agents.defaults.workspace`, falls fehlend.

**Nach Deploy:** `python -m src.scripts.openclaw_doctor_vps` (oder im Container `openclaw doctor`) ausführen, dann Container neustarten – so prüfst du, ob die Config schema-konform ist und alle Modelle wählbar sind.

Referenz: [OpenClaw Config Schema](https://config.clawi.sh/), [Configuration Examples](https://docs.openclaw.ai/gateway/configuration-examples).
