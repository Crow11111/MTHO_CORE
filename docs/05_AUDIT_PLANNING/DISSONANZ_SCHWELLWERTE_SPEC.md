# Dissonanz-Schwellwerte – Spezifikation (Not-Aus)

**Stand:** 2026-03-03  
**Quelle:** GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md (Axiom 4), WELTFORMEL_KURZBEWERTUNG.md  
**Status:** Spec only – keine Implementierung im Code.

---

## 1. Operative Definition: Dissonanz

**Dissonanz** im Sinne des Not-Aus ist die **kumulierte logische Reibung**, ab der weitere Ausführung wertvolle Rechenleistung in nicht auflösbare Widersprüche pumpt („schwarzes Loch aus Unlogik“). Sie ist **nicht** identisch mit:

- **Shadow-Metrik** (z. B. `log_dissonance_score` in `engine_patterns.py`): Beobachtung ohne Steuerung.
- **Semantischer Drift** (`temporal_validator`: Distanz 0.3/0.8): Bewertung eines einzelnen Dokuments vs. Korpus.

Operativ bedeutet Dissonanz hier **mindestens eines** der folgenden, über einen definierten Zeit-/Skopenraum aggregiert:

| Dimension | Bedeutung | Beispiel |
|-----------|-----------|----------|
| **Daten-Inkonsistenz** | Zustand von DB/Chroma/Input widerspricht erwarteter Invariante oder Ring-0-Direktive. | Core-Directive fehlt in Chroma; Ring-Level widerspricht Zugriffsregel. |
| **Wiederholte Fehlschläge** | Gleicher Request/Agent/Task schlägt mehrfach hintereinander fehl. | Retry-Count überschreitet sinnvollen Backoff; keine Konvergenz. |
| **Token-/Ressourcen-Überlast** | Budget (Token, Zeit, Speicher) wird systematisch überschritten oder aufgebraucht ohne Ergebnis. | Session verbraucht Budget ohne `[STATUS: COMPLETED]`; Agent bleibt in Retry-Schleife. |
| **Delta-Entropie-Proxy** | Abweichung „erwarteter vs. erreichter Zustand“ wird groß; System entfernt sich von konsistentem Ziel. | Erwarteter Kontext (z. B. Retrieval-Ergebnis) weicht stark ab; Validierung schlägt wiederholt fehl. |

**Not-Aus:** Ab einem definierten Schwellenwert wird die **Ausführung verweigert** (kein weiterer Retry, kein Delegieren an denselben Pfad). Optional: klare Fehlermeldung, Log, Rollback-Punkt.

---

## 2. Schwellen-Vorschläge mit Metriken

### Schwellen-Vorschlag A: Pro Request (Request-Scope)

| Metrik | Schwellenwert | Aktion |
|--------|----------------|--------|
| **Retry-Count** | ≥ 5 (Fibonacci-nahe: 5) fehlgeschlagene Versuche für denselben Request. | Not-Aus für diesen Request; Response „Dissonanz-Schwelle überschritten (Retry)“. |
| **Token-Budget-Überschreitung** | Verbrauch > 120 % des zugewiesenen Request-Budgets. | Not-Aus; keine weiteren Tool-Calls für diesen Request. |
| **Validierungsfehler** | ≥ 2 harte Validierungsfehler (z. B. `temporal_validator.drift_warning` oder Invarianten-Check). | Not-Aus für Request; Log mit Kontext. |

**Skope:** Ein einzelner Request (z. B. API-Call, eine User-Nachricht). Kein Session-Memory zwischen Requests.

---

### Schwellen-Vorschlag B: Pro Session (Session-Scope)

| Metrik | Schwellenwert | Aktion |
|--------|----------------|--------|
| **Fehlerrate** | > 33 % der Requests in der Session enden mit Fehler (z. B. 3 von 8). | Not-Aus für die Session; neue Session erforderlich oder expliziter Reset. |
| **Kumulierte Retries** | Summe Retries in Session ≥ 13 (Fibonacci). | Not-Aus; Session als „dissonant“ markieren, keine weiteren Delegationen. |
| **Delta-Entropie-Proxy (Session)** | Running Average der „Distanz zu erwartetem Zustand“ (z. B. Retrieval-Qualität, Konsistenz-Checks) > 0.8 über die letzten N Requests. | Not-Aus; Hinweis auf Kontext-Drift oder inkonsistente Datenbasis. |

**Skope:** Eine Session (z. B. ein Chat, ein Orchestrator-Durchlauf mit mehreren Agenten-Runden). State wird pro Session gehalten.

---

### Schwellen-Vorschlag C: Pro Agent / Pfad (Agent-Scope) — **User-Entscheidung: gewählt**

| Metrik | Schwellenwert | Aktion |
|--------|----------------|--------|
| **Agent-spezifische Fehlerrate** | Ein bestimmter Agent (oder Subagent-Typ) liefert in der Session ≥ 3× `[FAIL]` oder Exception. | Not-Aus für **diesen** Agenten in dieser Session; Orchestrator wählt anderen Pfad oder bricht ab. |
| **Konvergenz-Ausfall** | Nach 2 Iterationen (Produzent → Auditor → Re-Iteration) kein `[SUCCESS]`; erneutes `[FAIL]` vom Auditor. | Not-Aus für diese Task-Kette; Rückmeldung an User/Orchestrator. |

**Skope:** Ein Agent oder eine feste Agenten-Kette (z. B. Produzent + ND-Analyst). Verhindert Endlosschleifen in der Agenten-Dissonanz.

**User-Input (für Prozess/Bewertung, nicht 1:1 übernommen):** Präferenz Vorschlag C; Erfahrung: mit 1.–2. Prompt sitzen, 3. meist nicht → **Three Strikes → raus**. Team Lead neuer Versuch (3 Strikes), danach Fail nach oben oder ganzes Team auswechseln (mit anderem Tokendruck). Shadow-Mode + Tracking; Auswertung morgen nach 12 Uhr, dann sanftes Rollout.  
*Die verbindliche Fassung (inkl. möglicher Kritik/Verbesserung) wird nach Bewertung durch Council/Judge ergänzt (siehe `docs/04_PROCESSES/USER_ANMERKUNGEN_PROZESS.md`).*

**Bewertung (Judge):** User-Input ist konsistent mit Vorschlag C (Agent-Scope, 3× FAIL). Three Strikes entspricht der Spec-Metrik „≥ 3× `[FAIL]`“. Team-Lead-Neustart mit erneut 3 Strikes und danach Eskalation oder Team-Tausch ergänzt die Spec sinnvoll und begrenzt Endlosschleifen. Risiko: „anderer Tokendruck“ bei Team-Tausch in der Implementierung konkret definieren (z. B. Budget-Anpassung). Shadow-Mode und Auswertung nach 12 Uhr vor Rollout entsprechen Abschnitt 3 und sind tragbar.

**Bewertete Fassung (Judge), verbindlich:**  
(1) **Schwellen-Regel:** Drei Fehlschläge (`[FAIL]`/Exception) desselben Agents in der Session → Not-Aus für diesen Agent; Orchestrator wechselt Pfad oder übergibt an Team Lead.  
(2) **Team-Lead-Neustart:** Der Team Lead erhält einen neuen Versuch mit wiederum drei Strikes; danach entweder **Eskalation nach oben** (Fail an Orchestrator/User) oder **Austausch des gesamten Teams** (andere Agenten-Kombination, angepasster Tokendruck).  
(3) **Shadow-Mode & Rollout:** Schwellen werden zunächst nur gegengerechnet und getrackt (Shadow-Mode); keine Not-Aus-Auslösung vor Auswertung. **Auswertung** am Folgetag nach 12 Uhr; je nach Ergebnis **erste Überführung** in sanftes Rollout (Feature-Flag, Ring-Level ≥ 1 zuerst).

---

## 3. Empfehlung Test / Rollout

- **Keine Produktion zuerst:** Schwellwerte nicht direkt in Produktion aktivieren. Zuerst **nur loggen** (Shadow-Mode): gleiche Metriken berechnen und in Log/Telemetrie schreiben, ohne Not-Aus auszulösen.
- **Dry-Run / Feature-Flag:** Ein Flag (z. B. `DISSONANCE_EMERGENCY_STOP_ENABLED=false`) steuert, ob bei Überschreitung nur geloggt wird oder tatsächlich verweigert wird. Rollout: zuerst Ring-Level ≥ 1 (nicht Ring-0), dann optional Ring-0.
- **Stub / Test-Session:** In Tests (z. B. pytest oder integrierter Test-Orchestrator) künstlich Retry-Count, Fehlerrate oder Delta-Entropie-Proxy erhöhen und prüfen, dass bei aktivem Flag die Verweigerung und das erwartete Log/Response kommen.
- **Ring-Level:** Not-Aus zuerst nur für „nicht-kritische“ Ring-Level (z. B. Experimente, Forge) erlauben; Ring-0 (Core, Council) erst nach Validierung der Schwellen und False-Positive-Rate.

**Zeitplan (User-Go):** Shadow-Mode aktiv; Tracking gegenrechnen. **Auswertung:** morgen nach 12 Uhr. Je nach Ergebnis **erste Überführung** in sanftes Rollout (Feature-Flag, Ring ≥ 1 zuerst).

**Abgrenzung:** Diese Spec definiert **nur** Schwellen und Metriken. Trigger-Ort (API-Gateway, Orchestrator, Agent-Wrapper), Rollback und genaue Fehlercodes bleiben einer Implementierungs-Phase vorbehalten.
