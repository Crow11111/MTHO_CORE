# AGENTS.md — OMEGA CORE

Einstieg für Cloud-/KI-Agenten. Für Architektur und Theorie → `KANON_EINSTIEG.md`, `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`.

## Cursor Cloud specific instructions

### Services Overview

| Service | Port | Start Command |
|---------|------|---------------|
| **FastAPI Backend** | 8000 | `source .venv/bin/activate && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000` |
| **React Frontend** | 3000 | `cd frontend && npx vite --port=3000 --host=0.0.0.0` |

### Gotchas & Caveats

- **Python venv**: The project uses a `.venv` in the workspace root. Always activate with `source .venv/bin/activate` before running Python commands.
- **Frontend binary permissions**: After `npm install` in `frontend/`, you may need to run `chmod +x frontend/node_modules/.bin/* && find frontend/node_modules -name "esbuild" -type f -path "*/bin/*" -exec chmod +x {} \;` to fix esbuild/vite permission issues.
- **`.env` file**: Copy from `.env.template`. The backend starts without external service credentials — it gracefully degrades when `HASS_URL`, `GEMINI_API_KEY`, etc. are not set.
- **Extra Python deps not in `requirements.txt`**: The backend imports `chromadb`, `langchain-ollama`, `langchain-google-genai`, `google-genai`, `aiohttp`, `psutil`, and `pytest-asyncio` which are not listed in `requirements.txt`. These must be installed separately.
- **Frontend TS lint**: `cd frontend && npx tsc --noEmit` — there are 2 pre-existing type errors in `src/App.tsx` (German string literals vs English union types).
- **Tests**: `python -m pytest tests/ --ignore=tests/test_arbitration.py` — `test_arbitration.py` has a broken import (`_reset_jobs_db`). 4 other tests fail due to pre-existing code issues, not environment problems.
- **ChromaDB**: Runs locally by default (uses `data/chroma_db` path). No Docker or external ChromaDB needed for dev.

### Lint / Test / Build / Run

See `README.md` for quickstart. Key commands:

```bash
# Backend
source .venv/bin/activate
python -m pytest tests/ --ignore=tests/test_arbitration.py   # tests
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000  # run

# Frontend
cd frontend
npx tsc --noEmit   # lint
npm run build       # build
npx vite --port=3000 --host=0.0.0.0   # dev server
```
