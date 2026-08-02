# IncidentZero AI

**Autonomous Multi-Agent SOC Investigation Platform**
*Don't search logs. Understand attacks.*

**Demo:** [Google Drive walkthrough and assets](https://drive.google.com/file/d/1ZwMlSd8y2OW5Pq1Kjt8K_oRka41zSdiU/view?usp=sharing)

**Docker Hub:** [Frontend image](https://hub.docker.com/r/jatinshewale06/incidentzero-frontend) · [Backend image](https://hub.docker.com/r/jatinshewale06/incidentzero-backend)

IncidentZero AI is a working, self-hostable security platform where a
multi-agent AI system, reasoning through **Gemma4**, investigates a security
incident the way a senior Tier-3 SOC analyst would: it plans what evidence it
needs, pulls it from **Elasticsearch** via a real **MCP** tool layer,
correlates it, reconstructs the attack chain, maps it to **MITRE ATT&CK**,
scores the risk, translates the findings into **OWASP Top 10** and
**CIS Controls** themes, recommends a response, and explains every conclusion
with cited evidence.

This is a complete, runnable full-stack application, not a slide deck.
It ships with:

- A **FastAPI backend** with 11 real agents, SQLite/Postgres persistence, JWT auth, and WebSocket live-progress streaming
- A **React 19 + Vite + Tailwind** frontend with a real command-center UI
- A **local rule-based detection engine** so the whole pipeline works out of the box with zero external services
- Optional, real integrations you can switch on: **Elasticsearch** for log storage/search, **Ollama/Gemma4** for LLM reasoning, and a standalone **MCP server** for external MCP clients
- A realistic simulated enterprise dataset, **Operation ShadowFox**, a phishing -> PowerShell -> persistence -> credential theft -> C2 attack chain hidden inside normal traffic

New here? Start with [`SETUP.md`](./SETUP.md) for step-by-step laptop installation.

---

## How it works

```text
User investigation request ("Investigate FIN-PC-023")
        |
        v
   Planner Agent  -> decides which evidence categories are needed
        |
        v
   Elastic/MCP Agent  -> pulls auth / process / network / DNS / Sysmon / registry / file events
        |
        v
   Threat Hunter Agent -> rule-based detections (encoded PowerShell, LSASS access, persistence, C2 beaconing...)
        |
        +--> IOC Agent            -> cross-references indicators against threat intel
        +--> Timeline Agent       -> merges everything into a chronological story
        +--> Attack Graph Agent   -> builds a node/edge relationship graph
        +--> MITRE Agent          -> maps findings to ATT&CK techniques
        +--> Benchmark Agent      -> maps the same evidence to OWASP Top 10 and CIS Controls themes
        +--> Risk Agent           -> computes an overall risk score
        +--> Response Agent       -> recommends immediate + long-term actions
        `--> Explainability Agent -> validates every finding and writes the narrative (via Gemma4 if available)
        |
        v
   Report Agent  -> technical / executive markdown report
```

Every step streams live over WebSocket to the frontend, so you watch the
agents work in real time, exactly like the architecture in `docs/`.

## Why it still works without Gemma4 or Elasticsearch

Production security tools cannot depend on a GPU or an external cluster just
to boot. So every smart layer has a deterministic fallback:

| Layer | With real service | Without (default) |
|---|---|---|
| Log storage/search | Elasticsearch cluster (`ELASTIC_ENABLED=true`) | Local CSV data engine (pandas), same query interface |
| Reasoning / narrative | Gemma4 via Ollama (`GEMMA_ENABLED=true`) | Rule-based planner + deterministic narrative generator |
| Tool access | Real MCP server (`app/mcp_layer/server.py`) | In-process tool client (same tool functions) |

Flip the flags in `backend/.env` any time. No agent code changes needed.

## Project layout

```text
IncidentZero-AI/
|-- backend/            FastAPI app, agents, Gemma/MCP/Elastic integrations, dataset
|-- frontend/           React + Vite + Tailwind SOC dashboard
|-- docker-compose.yml  One-command orchestration (+ optional Elastic/Ollama profiles)
|-- SETUP.md            Step-by-step laptop setup guide
`-- docs/ARCHITECTURE.md Full technical architecture reference
```

## Quick start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **http://localhost:5173**, click **Launch Dashboard**, and run:
`Investigate suspicious activity on FIN-PC-023` - that's the ShadowFox
attack, and IncidentZero AI will find it end-to-end using nothing but the
bundled dataset.

Full details, troubleshooting, and how to enable real Elasticsearch/Gemma4
are in **[SETUP.md](./SETUP.md)**.

## License

MIT License - see [LICENSE](./LICENSE).
