# Tool-Audit-Liste (Phase 2) – Rohentwurf

**Stand:** 2026-03-03 | **Zweck:** Grundlage für Security/API-Prüfung. Keine Implementierung.

---

## 1. Bereits im Einsatz / in Docs erwähnt

| Name | Zweck | Wo |
|------|--------|-----|
| **Tampermonkey** | Browser-Extension: Markierter Text → ATLAS TTS (Strg+Shift+S). GM_xmlhttpRequest → localhost:8000/api/atlas/speak | docs/03_INFRASTRUCTURE/TAMPERMONKEY_TTS_INTEGRATION.md |
| **ElevenLabs** | TTS-API; Rollen (atlas_dialog, therapeut, analyst). Backend: atlas_voice.py, voice_config | src/api/routes/atlas_voice.py, .env ELEVENLABS_* |
| **Streamlit** | Dev-Agent-Console, lokale Web-UI ohne Cursor-Quota | src/ui/dev_agent_console.py, DEV_AGENT_UND_SCHNITTSTELLEN.md |
| **React/Vite** | Frontend Dashboard, WebSocket Chat, Backend-Status | frontend/, BACKEND_INTEGRATION.md |
| **ChromaDB** | Vektor-Store, Session-Turns, Core-Directives, Embeddings | src/config/engine_patterns.py, ATLAS_CHROMADB_SCHEMA.md |
| **Ollama** | Lokales LLM (langchain_ollama), Scout/HA-Kontext | llm_interface.py, usb_microphone_research.md |
| **Gemini (Google AI)** | LLM-Provider, OC Admin, Modell-IDs in OPENCLAW | .cursor/skills/gemini-api-dev/SKILL.md, OPENCLAW_ADMIN_ARCHITEKTUR.md |
| **LangChain** | ChatOllama, ChatGoogleGenerativeAI, Message-Ketten | src/ai/llm_interface.py, requirements.txt |
| **Extract-Pipelines** | Textauswertung: extract_topics (heuristisch), extract_pipeline_v4, extract_nd_insights, ingest_session_log | src/scripts/ingest_session_log.py, extract_pipeline_v4.py, extract_nd_insights.py |
| **MCP** | cursor-ide-browser (Browser-Automation), deploy_mcp.py (VPS Port 8001) | mcps/cursor-ide-browser, src/scripts/deploy_mcp.py |
| **OpenClaw** | OC Admin (Gateway, WhatsApp, Nexos), ATLAS→OC über openclaw_client | KANAL_ATLAS_OC.md, OPENCLAW_ADMIN_ARCHITEKTUR.md |

---

## 2. Empfohlene Tools für ATLAS (Textauswertung, Zusammenfassung, Extensions)

| Name | Zweck | Priorität | Begründung / Integration |
|------|--------|-----------|---------------------------|
| **LLM-basierte Zusammenfassung (vorhanden)** | Lange Texte/Logs komprimieren vor Chroma/OC | P0 | Bereits über Gemini/Ollama abdeckbar; kein neues Tool, nur klare Pipeline (z. B. summarise → add_session_turn). |
| **TIE/ND-Extract (Codebase)** | Strukturierte Extraktion aus Journallen/Transkripten | P0 | extract_pipeline_v4 + extract_nd_insights ausbauen statt neuer externer Service; bleibt in ATLAS-Pipeline, keine zusätzliche API. |
| **Tampermonkey (erweitert)** | Optional: Shortcuts für weitere Stimmen oder „Zusammenfassen & TTS“ | P1 | Gleiche Extension; neues Endpoint z. B. POST /api/atlas/summarise-and-speak (Backend macht Summarise + TTS). Security: weiterhin nur localhost. |
| **Cursor Rules/Skills** | Keine Installation; .cursorrules + .cursor/skills bereits genutzt | P0 | Keine neuen Tools; Dokumentation prüfen, ob alle Text-/Summarize-Flows in Rules abgedeckt sind. |
| **tiktoken / Token-Zählung** | Token-Budget, Circuit Breaker, Kostenkontrolle | P1 | In Docs erwähnt (ATLAS_CORE_BRAIN_REGISTR); für Summarize-Pipeline sinnvoll (Max-Length vor LLM-Call). Prüfung: API-Key/Netzwerk nicht nötig, nur lokale Zählung. |
| **Browser-Extension (nur Tampermonkey)** | Keine zweiten Extension-Stacks; alles in einem Userscript | P1 | Reduziert Angriffsfläche; Tampermonkey @connect auf localhost beschränkt lassen. |

---

## 3. Explizit nicht empfohlen / Abgrenzung

- **Externe Summarizer-APIs (z. B. separate SaaS):** Unnötig; Gemini/Ollama im Backend reicht, vermeidet zusätzliche Keys und Latenz.
- **Neue Browser-Extensions neben Tampermonkey:** Eine Extension pro Funktion (TTS, ggf. Summarise) in einem Skript halten.
- **Redis/Externe Cache für Textauswertung:** Nicht in Scope; Chroma + Backend-Logik ausreichend.

---

## 4. Security/API-Prüfung – Stichpunkte

- **Tampermonkey:** @connect localhost/127.0.0.1; kein Sensitive-Data in Userscript; Backend /api/atlas/speak nur lokal erreichbar halten.
- **ElevenLabs:** API-Key in .env, nicht im Frontend; Rate-Limits prüfen.
- **MCP cursor-ide-browser:** Nur in vertrauenswürdigen Umgebungen; Lock/Unlock-Workflow einhalten.
- **Neue Endpoints (z. B. summarise-and-speak):** Gleiche Auth-Strategie wie /api/atlas/speak (lokaler Aufruf); keine Exposition nach außen.

---

## 5. Security/DB/API-Prüfung (detailliert)

- **Vollständige Bewertung:** `docs/05_AUDIT_PLANNING/TOOL_AUDIT_EMPFEHLUNG.md` (security-expert). P0: Auth für Webhooks/OC/db_backend; WhatsApp HMAC; HA Shared-Secret.

## 6. Verweise

- TTS-Integration: `docs/03_INFRASTRUCTURE/TAMPERMONKEY_TTS_INTEGRATION.md`
- Chroma/Schema: `docs/02_ARCHITECTURE/ATLAS_CHROMADB_SCHEMA.md`
- Dev-Agent: `docs/02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md`
- OC-Kanal: `docs/02_ARCHITECTURE/KANAL_ATLAS_OC.md`
