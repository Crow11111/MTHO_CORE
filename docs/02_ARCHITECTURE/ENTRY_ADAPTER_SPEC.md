<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Entry Adapter Spec (GQA F13)

**Status:** Implementiert
**Priorität:** Vor F5 (Gravitator) – Gravitator benötigt normalisierte Inputs.

---

## 1. Zweck

Der Entry Adapter normalisiert heterogene Webhook-Payloads aus verschiedenen Quellen zu einem einheitlichen `NormalizedEntry`. Downstream-Komponenten (Gravitator, Triage, etc.) erhalten damit einen flachen, quellenunabhängigen Input.

---

## 2. Vertrag

### 2.1 NormalizedEntry (Pydantic)

```python
class NormalizedEntry(BaseModel):
    source: str       # "whatsapp" | "ha" | "oc" | "api"
    payload: dict     # flach, kein Session-Ref
    timestamp: str    # ISO8601
    auth_ctx: dict    # optional: {method, client_id}
```

### 2.2 API

```python
def normalize_request(source: str, raw_payload: Any, auth_ctx: dict | None = None) -> NormalizedEntry
```

- **source:** Einer von `"whatsapp"`, `"ha"`, `"oc"`, `"api"`.
- **raw_payload:** Roher Request-Body (dict, list, oder JSON-kompatibel).
- **auth_ctx:** Optional. Enthält `method` (z.B. `"bearer"`, `"x-api-key"`) und ggf. `client_id`.
- **Rückgabe:** `NormalizedEntry` mit ISO8601-Timestamp, flachem Payload, kein Session-Ref.

---

## 3. Source-Mapping

| Source    | Rohformat (Beispiel) | Normalisierter Payload (flach) |
|-----------|----------------------|--------------------------------|
| `ha`      | `{action, message, data, user_id}` | `{action, text, user_id, ...}` – `text` = message |
| `ha`      | `{text}` (inject_text, assist) | `{text}` |
| `ha`      | `{text, context}` (forwarded_text) | `{text, context}` |
| `whatsapp`| Nested `message.conversation`, `extendedTextMessage.text` | `{text, sender, has_audio, ...}` |
| `oc`      | rat_submission JSON | `{topic, body, from, type}` |
| `api`     | Direkter API-Body | Unverändert flach übernommen |

**Regel:** `payload` ist immer ein flaches dict. Keine verschachtelten Session- oder Request-Objekte.

---

## 4. Fehlerbehandlung

- Ungültiger `source` → `ValueError`.
- `raw_payload` kein dict → Konvertierung zu `{"raw": raw_payload}` (Fallback).
- `auth_ctx` fehlt → `{}`.

---

## 5. Integration

1. Webhook empfängt Request.
2. Ruft `normalize_request(source, raw_payload, auth_ctx)` auf.
3. Übergibt `NormalizedEntry` an Downstream (Gravitator, Triage, etc.).

**Integration (2026-03-06):** `whatsapp_webhook.receive_whatsapp`, `ha_webhook.receive_ha_action` – beide nutzen ausschließlich `normalize_request()`; der Adapter ruft **niemals** OMEGA_ATTRACTOR oder Kern-Logik direkt auf. Ausgabe geht an Triage/Gravitator (ggf. nach Takt-0-Gate).

---

## 6. Abhängigkeiten

- **Vor:** Keine (Entry Adapter ist Einstiegspunkt).
- **Nach:** Takt-0-Gate (optional), F5 Gravitator, Triage-Pipeline.

---

## 7. Tesserakt-Topologie

Der Entry Adapter ist die **Membran** des Tesserakts: Außenhülle, isoliert von der Kern-Logik. Siehe `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` und `docs/CORE_GENESIS_FINAL_ARCHIVE.md` (§4).
