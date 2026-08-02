# IncidentZero AI — Setup Guide

This walks you through running the full project on your own laptop (Windows,
macOS, or Linux). There are two paths:

- **[Path A — Run it directly](#path-a--run-it-directly-recommended-first)** (no Docker) — fastest way to see it working, best while you're exploring/developing
- **[Path B — Run it with Docker](#path-b--run-it-with-docker)** — one command, closer to how you'd deploy it

Either way, **it works with zero external services** out of the box (no
Elasticsearch, no GPU, no API keys). Real Elasticsearch and real local Gemma
are both optional upgrades documented at the bottom.

---

## Prerequisites

| Tool | Version | Check with |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| Node.js | 20+ | `node --version` |
| npm | 10+ | `npm --version` |
| Docker (optional, Path B only) | latest | `docker --version` |

If you're missing any of these:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org (LTS version)
- Docker Desktop: https://www.docker.com/products/docker-desktop/

---

## Path A — Run it directly (recommended first)

### 1. Unzip the project

```bash
unzip IncidentZero-AI.zip
cd IncidentZero-AI
```

### 2. Start the backend

Open a terminal:

```bash
cd backend
python3 -m venv venv
```

Activate the virtual environment:
- **macOS / Linux:** `source venv/bin/activate`
- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate.bat`

Install dependencies and configure:

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

Generate the demo dataset (already included, but this regenerates it deterministically if you ever want to):

```bash
python scripts/generate_demo_data.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

You should see:

```
============================================================
  IncidentZero AI v1.0.0
  Mode: DEMO
  Elasticsearch: disabled — using local CSV data engine
  Gemma (Ollama): disabled — using deterministic reasoning fallback
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this running. Open http://localhost:8000/docs to see the interactive
API docs (Swagger UI) — you can try every endpoint from there directly.

### 3. Start the frontend

Open a **second** terminal (leave the backend running in the first):

```bash
cd frontend
npm install
cp .env.example .env        # Windows: copy .env.example .env
npm run dev
```

You should see:

```
VITE ready
➜  Local:   http://localhost:5173/
```

### 4. Use it

Open **http://localhost:5173** in your browser.

1. Click **Launch Dashboard**
2. In the "Launch a New Investigation" box, type (or keep the default):
   `Investigate suspicious activity on FIN-PC-023`
3. Click **Investigate** — you'll be taken to the investigation page and see
   the agent pipeline run live (Planner → Elastic → Threat Hunter → IOC →
   Timeline → Attack Graph → MITRE → Risk → Response → Explainability)
4. Explore the tabs: **Summary, Evidence, Attack Graph, Timeline, Response**
5. Visit **IOC Explorer** and **MITRE ATT&CK** in the sidebar (they show data
   for whichever investigation you last opened)
6. Try the **AI Assistant** tab and ask: *"What happened on this host?"*,
   *"Why is this IP malicious?"*, *"What should I do now?"*
7. Generate a report from the **Reports** page and export it as Markdown

That's the full "Operation ShadowFox" attack — a phishing email leading to
encoded PowerShell, persistence, credential access, and C2 beaconing — found
entirely by the rule-based detection engine bundled in the repo. No external
AI service required.

### Stopping everything

`Ctrl+C` in both terminals. To resume later, just re-activate the venv and
re-run `uvicorn app.main:app --reload` and `npm run dev`.

---

## Path B — Run it with Docker

From the project root:

```bash
docker compose up --build
```

This builds and starts:
- `backend` on **http://localhost:8000**
- `frontend` on **http://localhost:5173**

Both use the same zero-dependency local data engine as Path A. Open
http://localhost:5173 and follow steps 1–7 above.

To stop: `Ctrl+C`, then `docker compose down`.

### Docker Hub publish flow

If you want to publish the app images to Docker Hub, build and tag the backend and frontend separately. The Ollama image is pulled from Docker Hub; you normally do not push your own copy of it.

```bash
docker login

# From the project root
docker build -t jatinshewale06/incidentzero-backend:1.0.0 ./backend
docker build -t jatinshewale06/incidentzero-frontend:1.0.0 ./frontend

docker push jatinshewale06/incidentzero-backend:1.0.0
docker push jatinshewale06/incidentzero-frontend:1.0.0
```

If you want `docker compose` to use those published images, set:

```bash
export DOCKERHUB_NAMESPACE=jatinshewale06
export IMAGE_TAG=1.0.0
```

Then run:

```bash
docker compose up
```

---

## Optional: enable real Elasticsearch

By default, IncidentZero AI reads the demo dataset from CSV via a local
pandas-backed data engine. To point it at a real Elasticsearch cluster
instead (same query interface, zero agent code changes):

```bash
# 1. Start Elasticsearch
docker compose --profile elastic up -d elasticsearch

# 2. Load the dataset into it
cd backend
export ELASTIC_ENABLED=true          # Windows: set ELASTIC_ENABLED=true
export ELASTIC_URL=http://localhost:9200
python scripts/ingest_to_elastic.py

# 3. Tell the backend to use it
#    edit backend/.env:
#    ELASTIC_ENABLED=true
#    ELASTIC_URL=http://localhost:9200

# 4. Restart the backend
uvicorn app.main:app --reload
```

You now have real Elasticsearch indexes (`incidentzero-auth`,
`incidentzero-process`, `incidentzero-network`, etc.) backing every agent
query. You can browse them directly at http://localhost:9200 or point
Kibana at the same cluster.

---

## Optional: enable real Gemma (via Ollama)

By default, the reasoning/narrative layer uses a deterministic template
generator (still fully grounded in evidence — just not LLM-written prose).
To use a real local Gemma model:

### 1. Install Ollama

https://ollama.com/download — available for macOS, Windows, and Linux.

### 2. Pull a Gemma model

```bash
ollama pull gemma4
```

(Smaller laptops: try `gemma2:2b`. More powerful machines: `gemma3:27b` if
you have the VRAM/RAM for it — just update `GEMMA_MODEL` to match.)

### 3. Start Ollama

```bash
ollama serve
```

(On macOS/Windows the Ollama app usually does this automatically after
installation.)

### 4. Point the backend at it

Edit `backend/.env`:

```
GEMMA_ENABLED=true
OLLAMA_URL=http://localhost:11434
GEMMA_MODEL=gemma4
```

Restart the backend. The **Settings** page in the app (and the topbar status
pill) will now show "Gemma Online" — investigation summaries, chat answers,
and reports will be written by Gemma, still strictly grounded in the
evidence agents retrieved (see `backend/app/gemma/prompts.py` for the
guardrails in the system prompt).

If Ollama becomes unreachable mid-session, every agent call automatically
falls back to the deterministic path — the app never crashes because Gemma
isn't available.

---

## Optional: run the standalone MCP server

The exact same security tools (`search_logs`, `get_process_tree`,
`lookup_ioc`, `search_mitre`, …) are also exposed over the real Model
Context Protocol, so any MCP client (Claude Desktop, Claude Code, etc.) can
query your security data directly:

```bash
cd backend
python -m app.mcp_layer.server
```

Or inspect it interactively:

```bash
pip install "mcp[cli]"
mcp dev app/mcp_layer/server.py
```

---

## Running the tests

```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

---

## Troubleshooting

**`ModuleNotFoundError` on backend start**
You likely forgot to activate the virtual environment. Re-run the
`source venv/bin/activate` (or Windows equivalent) step, then
`pip install -r requirements.txt` again.

**Frontend shows "Can't reach the backend"**
Make sure `uvicorn` is running on port 8000 and that
`frontend/.env` has `VITE_API_URL=http://localhost:8000`. If you changed the
backend port, update this file to match.

**`bcrypt` install errors on Windows**
Make sure you're on Python 3.11+ and pip is up to date
(`python -m pip install --upgrade pip`) before `pip install -r requirements.txt`.

**Port already in use**
Something else is using 8000 or 5173. Stop it, or run on different ports:
`uvicorn app.main:app --reload --port 8001` and update
`frontend/.env` accordingly (and `frontend -- --port 5174` for Vite).

**Investigation seems stuck on "Idle" agents**
The pipeline runs as a FastAPI background task, driven live over WebSocket.
If your browser blocks WebSocket connections (corporate proxy, some VPNs),
the investigation still completes on the backend — refresh the page after a
few seconds and the Summary/Evidence/Timeline tabs will populate from the
REST API even without the live view.

**Elasticsearch container won't start / low memory**
Elasticsearch needs ~1GB+ free RAM. Lower `ES_JAVA_OPTS` in
`docker-compose.yml` further, or skip real Elasticsearch — the local data
engine is functionally equivalent for this dataset size.

---

## What to explore next

- `backend/app/agents/hunter_agent.py` — the detection rules; add your own
- `backend/datasets/` — swap in your own CSVs (keep the same columns) to
  investigate a different scenario
- `backend/app/gemma/prompts.py` — tune how Gemma reasons and writes
- `frontend/src/pages/` — every page maps 1:1 to a backend route; easy to extend

See [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) for the full technical
reference.
