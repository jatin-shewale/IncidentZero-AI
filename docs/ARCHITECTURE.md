# IncidentZero AI — Architecture Reference

This document maps the system as actually implemented. Where the original
product brief (multi-part hackathon spec) called for something that needs
external infrastructure (GPUs, a live Elastic cluster), this section says so
explicitly and explains the fallback that ships instead.

## 1. High-level architecture

```
                         React 19 + Vite + Tailwind (frontend/)
                                       │  REST + WebSocket
                                       ▼
                              FastAPI backend (backend/app)
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                 ▼
              Agent Orchestrator   SQLite/Postgres    WebSocket Manager
              (app/agents/orchestrator.py)  (investigations, evidence)  (live progress)
                     │
   ┌─────────────────┼──────────────────────────────────────────┐
   ▼                 ▼                 ▼                        ▼
Planner          Elastic/MCP       Threat Hunter    IOC · Timeline · Attack Graph
Agent            Agent             Agent            MITRE · Risk · Response ·
                                                     Explainability · Report
   │                 │
   ▼                 ▼
Gemma client    MCP tool client ──► data_engine (local CSV) OR elastic/queries.py (real ES)
(Ollama, optional, with
 deterministic fallback)
```

## 2. Backend (`backend/app`)

| Module | Responsibility |
|---|---|
| `main.py` | FastAPI app, CORS, router registration, `/ws/investigation/{id}` WebSocket, startup banner |
| `config/settings.py` | All env-driven configuration (single source of truth) |
| `core/database.py` | SQLAlchemy engine/session, `init_db()` seeds the demo analyst account |
| `core/security.py` | bcrypt password hashing + JWT (demo-mode auth is permissive by design — see below) |
| `core/websocket.py` | Per-investigation WebSocket connection manager / broadcaster |
| `models/` | SQLAlchemy models: `User`, `Investigation`, `AgentExecution`, `Evidence` |
| `schemas/` | Pydantic request/response contracts |
| `api/routes/` | `auth`, `investigations`, `agents`, `chat`, `reports`, `analytics` |
| `agents/` | The 11 agents (below) + `orchestrator.py` |
| `gemma/` | Ollama HTTP client, prompt templates, tool schemas |
| `mcp_layer/` | Real MCP server (`server.py`, FastMCP) + in-process client (`client.py`) used by agents |
| `elastic/` | `client.py` (elasticsearch-py wrapper), `queries.py` (ES-backed store), `mappings.py` (index defs) |
| `data_engine/` | `local_store.py` — pandas-backed store with the **same method signatures** as `elastic/queries.py` |
| `services/` | `threat_service.get_data_engine()` (selects local vs ES), `investigation_service`, `report_service` |
| `datasets/` | Operation ShadowFox CSVs |
| `scripts/` | `generate_demo_data.py`, `ingest_to_elastic.py` |

### The 11 agents (`backend/app/agents/`)

1. **planner_agent** — turns a natural-language request into a required-evidence plan (Gemma if available, keyword-based fallback otherwise)
2. **elastic_agent** — pulls evidence for each required category via the MCP tool client, correctly scoped to the investigated host
3. **hunter_agent** — deterministic detection rules (encoded PowerShell, Office→shell spawning, unsigned binaries, LSASS access, registry Run-key persistence, malicious DNS/IP resolution via threat intel, anomalous external auth, C2 beaconing patterns) — each finding carries a MITRE technique ID, severity, confidence, source, and reason
4. **ioc_agent** — extracts IPs/domains/hashes from evidence, cross-references `threat_intelligence.csv`
5. **timeline_agent** — merges all evidence sources into one chronological story
6. **attack_graph_agent** — builds a node/edge relationship graph from process trees, DNS resolutions, network connections, and persistence/credential-access techniques
7. **mitre_agent** — attaches tactic/technique names from `mitre_attack.csv` to hunter findings
8. **risk_agent** — weights finding severities + host criticality into a 0–100 risk score
9. **response_agent** — turns findings + IOCs into concrete immediate/long-term actions
10. **explainability_agent** — drops any finding missing evidence/reason/confidence, then writes the investigation narrative (Gemma if available, deterministic composition otherwise)
11. **report_agent** — assembles the final technical/executive markdown report

`agents/orchestrator.py` runs all of the above in sequence as a FastAPI
background task, persists results, and broadcasts each step over
`/ws/investigation/{id}` so the frontend shows live agent status.

### Why detection is rule-based, not just "ask an LLM"

The brief calls for zero hallucination and cited evidence for every claim.
A pure "ask Gemma to find the attack" approach can't guarantee that. Instead,
`hunter_agent.py` implements literal Sigma-style detection logic — the same
approach real detection engineering uses — and Gemma (when enabled) is used
only for **narrating already-verified findings**, never for inventing them.
This is also why the system investigates correctly regardless of which host
you point it at, not just the scripted demo host.

### Demo mode vs. production mode

- **Demo mode** (default, `DEMO_MODE=true`): auth is permissive — API calls
  without a token are treated as the seeded `analyst@incidentzero.ai` user,
  so you can explore every endpoint immediately. SQLite is used.
- **Production hardening checklist**: remove the token-optional fallback in
  `core/security.get_current_user_email`, set a real `SECRET_KEY`, switch
  `DATABASE_URL` to Postgres, put the backend behind HTTPS, and enable
  `ELASTIC_ENABLED` against a properly access-controlled cluster.

## 3. Frontend (`frontend/src`)

React 19 + Vite + Tailwind, React Router for navigation, a small Context
(`store/InvestigationContext.jsx`) for the currently-active investigation ID,
and a WebSocket hook (`store/useInvestigationSocket.js`) for live pipeline
status.

| Page | Backend routes it calls |
|---|---|
| `Landing` | none (marketing/entry page) |
| `Dashboard` | `POST /api/investigations/create`, `GET /api/investigations`, `GET /api/analytics/overview` |
| `Investigations` | `GET /api/investigations` |
| `InvestigationDetail` | `GET /api/investigations/{id}`, `/timeline`, `/graph`, `/evidence`, `/mitre`, `/response`, plus the WebSocket |
| `IOCExplorer` | `GET /api/investigations/{id}/iocs` |
| `MitrePage` | `GET /api/investigations/{id}/mitre` |
| `AIChat` | `POST /api/chat` |
| `Reports` | `POST /api/reports/generate/{id}`, download via `/reports/generate/{id}/download` |
| `Analytics` | `GET /api/analytics/overview` |
| `Settings` | `GET /api/agents/status` (read-only view of current config) |

The attack graph (`components/graphs/AttackGraphView.jsx`) computes its own
layered layout client-side (BFS from the host node) so it renders correctly
for any investigation, not just the bundled scenario.

## 4. Data (`backend/datasets`)

`scripts/generate_demo_data.py` deterministically (seeded) generates a
realistic day of enterprise telemetry for **NovaFinance Technologies** across
7 event categories, with the **Operation ShadowFox** attack chain — phishing
→ macro → encoded PowerShell → payload download → registry persistence →
LSASS credential access → C2 beaconing → attempted lateral movement —
seeded at realistic timestamps inside otherwise-normal traffic. Increase the
loop density in that script to scale up toward production-scale volumes
(the spec's target of 10k+ normal / 200 suspicious / 50 attack events);
the shipped defaults are tuned for fast local iteration.

## 5. Known simplifications (be upfront about these)

- **MCP protocol vs. in-process calls**: agents call `mcp_layer/client.py`
  directly (same process, no IPC) for speed and reliability during a live
  investigation. The *real* MCP protocol server (`mcp_layer/server.py`,
  built on the official `mcp` SDK's FastMCP) exposes the identical tool
  surface for external MCP clients — it's a genuine, separately runnable MCP
  server, just not on the hot path of a single investigation run.
- **Gemma function-calling**: `gemma/tools.py` defines OpenAI-style tool
  schemas for models that support structured tool calling through Ollama.
  The shipped agents don't depend on this path being available — they use
  direct function calls into the data engine — so the system works with
  any Gemma variant, including ones without native tool-calling support.
- **LangGraph**: the spec mentions LangGraph/Google ADK as an orchestration
  option. The orchestrator here is a plain async function with explicit
  steps and WebSocket events — simpler to read and debug, and sufficient at
  this pipeline's complexity. Swapping in LangGraph would mean rewriting
  `agents/orchestrator.py` as a `StateGraph`; every individual agent
  function is already a clean, swappable unit if you want to do that.
- **Vector DB / RAG over prior incidents**: not implemented. The "long-term
  memory" described in the original brief (similar-incident search) would
  be a natural next addition — e.g. embed each `Investigation.summary` and
  query with a vector store when a new investigation starts.
