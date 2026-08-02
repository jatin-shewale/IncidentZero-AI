"""
Agent Orchestrator — the central brain of IncidentZero AI.

Runs the full investigation pipeline end-to-end:

    Planner -> Elastic/MCP collection -> Threat Hunter -> IOC -> Timeline
    -> Attack Graph -> MITRE -> Risk -> Response -> Explainability -> Report

Persists results to the database and broadcasts live progress over
WebSocket to /ws/investigation/{id} so the frontend can show each agent
"thinking" in real time, exactly like the Part 3/4 spec describes.
"""
import asyncio
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.incident import Investigation, AgentExecution
from app.models.evidence import Evidence
from app.core.websocket import manager

from app.agents import (
    planner_agent, elastic_agent, hunter_agent, ioc_agent, timeline_agent,
    attack_graph_agent, mitre_agent, risk_agent, response_agent,
    explainability_agent, report_agent, benchmark_agent,
)

PIPELINE_STEPS = [
    "Planner", "Elastic", "Threat Hunter", "IOC Intel", "Timeline",
    "Attack Graph", "MITRE", "Risk Engine", "Response", "Explainability",
]

# In-memory cache of the last fully-computed investigation result, keyed by
# investigation_id — avoids re-querying the DB for every sub-resource call
# (timeline / graph / mitre / response endpoints) during a demo session.
_RESULT_CACHE: dict = {}


async def _emit(investigation_id: str, event_type: str, data: dict):
    await manager.broadcast(investigation_id, {"type": event_type, **data})


def _log_execution(db: Session, investigation_id: str, agent_name: str, status: str,
                    input_data=None, output_data=None, ms: int = 0):
    exec_row = AgentExecution(
        investigation_id=investigation_id,
        agent_name=agent_name,
        status=status,
        input=json.dumps(input_data, default=str)[:4000] if input_data else None,
        output=json.dumps(output_data, default=str)[:4000] if output_data else None,
        time_taken_ms=ms,
    )
    db.add(exec_row)
    db.commit()


async def run_investigation(db: Session, investigation_id: str, query: str, host: str):
    """Runs synchronously (agents are fast/local) but yields control between
    steps and emits WebSocket events so a connected frontend sees live progress."""

    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise ValueError(f"Investigation {investigation_id} not found")

    inv.status = "investigating"
    db.commit()
    await _emit(investigation_id, "status", {"status": "investigating"})

    # 1. PLANNER
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Planner"})
    the_plan = planner_agent.plan(query, host)
    _log_execution(db, investigation_id, "Planner", "done", {"query": query}, the_plan, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Planner", "output": the_plan})
    await asyncio.sleep(0.15)

    # 2. ELASTIC / MCP COLLECTION
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Elastic"})
    evidence_raw = elastic_agent.collect(host, the_plan["required_data"])
    counts = {k: len(v) for k, v in evidence_raw.items()}
    _log_execution(db, investigation_id, "Elastic", "done", the_plan["required_data"], counts, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Elastic", "output": counts})
    await asyncio.sleep(0.15)

    # 3. THREAT HUNTER
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Threat Hunter"})
    findings = hunter_agent.hunt(host, evidence_raw)
    _log_execution(db, investigation_id, "Threat Hunter", "done", None, {"finding_count": len(findings)}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Threat Hunter", "output": {"finding_count": len(findings)}})
    await asyncio.sleep(0.15)

    # 4. IOC INTEL
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "IOC Intel"})
    iocs = ioc_agent.extract(evidence_raw)
    _log_execution(db, investigation_id, "IOC Intel", "done", None, {"ioc_count": len(iocs)}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "IOC Intel", "output": {"ioc_count": len(iocs)}})
    await asyncio.sleep(0.15)

    # 5. TIMELINE
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Timeline"})
    timeline = timeline_agent.build(evidence_raw, findings)
    _log_execution(db, investigation_id, "Timeline", "done", None, {"event_count": len(timeline)}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Timeline", "output": {"event_count": len(timeline)}})
    await asyncio.sleep(0.15)

    # 6. ATTACK GRAPH
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Attack Graph"})
    graph = attack_graph_agent.build(host, evidence_raw, findings)
    _log_execution(db, investigation_id, "Attack Graph", "done", None,
                    {"nodes": len(graph["nodes"]), "edges": len(graph["edges"])}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Attack Graph", "output": {"nodes": len(graph["nodes"])}})
    await asyncio.sleep(0.15)

    # 7. MITRE
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "MITRE"})
    mitre = mitre_agent.map_techniques(findings)
    _log_execution(db, investigation_id, "MITRE", "done", None, {"technique_count": len(mitre)}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "MITRE", "output": {"techniques": [m["technique_id"] for m in mitre]}})
    await asyncio.sleep(0.15)

    # Benchmark view (OWASP / CIS)
    benchmark = benchmark_agent.summarize(findings)

    # 8. RISK ENGINE
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Risk Engine"})
    from app.data_engine.local_store import local_store
    host_row = next((h for h in local_store.hosts() if h["hostname"] == host), {})
    risk = risk_agent.score(findings, host_row.get("criticality", "Medium"))
    _log_execution(db, investigation_id, "Risk Engine", "done", None, risk, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "risk_update", {"value": risk["risk_score"]})
    await asyncio.sleep(0.15)

    # 9. RESPONSE
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Response"})
    response = response_agent.recommend(host, findings, iocs)
    _log_execution(db, investigation_id, "Response", "done", None, response, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Response", "output": response})
    await asyncio.sleep(0.15)

    # 10. EXPLAINABILITY (validation + narrative)
    t0 = time.time()
    await _emit(investigation_id, "agent_started", {"agent": "Explainability"})
    findings = explainability_agent.validate(findings)
    narrative = explainability_agent.narrate(investigation_id, host, findings, timeline)
    _log_execution(db, investigation_id, "Explainability", "done", None, {"validated": len(findings)}, int((time.time() - t0) * 1000))
    await _emit(investigation_id, "agent_done", {"agent": "Explainability", "output": {"narrative_ready": True}})

    # --- persist final investigation state ---
    confidence = round(sum(f["confidence"] for f in findings) / len(findings)) if findings else 0
    SEVERITY_LABEL_MAP = {"Critical": "crit", "High": "crit", "Medium": "warn", "Low": "ok"}
    inv.risk_score = risk["risk_score"]
    inv.confidence = confidence
    inv.severity = SEVERITY_LABEL_MAP.get(risk["severity"], "info")
    inv.status = "investigating_complete"
    inv.summary = narrative
    db.commit()

    # --- persist evidence rows ---
    db.query(Evidence).filter(Evidence.investigation_id == investigation_id).delete()
    for f in findings:
        db.add(Evidence(
            investigation_id=investigation_id,
            source=f["source"],
            event=f["finding"],
            severity=f["severity"],
            explanation=f["reason"],
            confidence=f["confidence"],
            raw_event=json.dumps(f.get("raw", {}), default=str),
        ))
    db.commit()

    result = {
        "investigation": {
            "id": investigation_id, "host": host, "risk_score": risk["risk_score"],
            "confidence": confidence, "severity": inv.severity, "summary": narrative,
        },
        "plan": the_plan,
        "findings": findings,
        "iocs": iocs,
        "timeline": timeline,
        "graph": graph,
        "mitre": mitre,
        "benchmarks": benchmark,
        "risk": risk,
        "response": response,
        "narrative": narrative,
    }
    _RESULT_CACHE[investigation_id] = result

    await _emit(investigation_id, "investigation_complete", {
        "risk_score": risk["risk_score"], "confidence": confidence, "severity": inv.severity,
    })
    return result


def get_cached_result(investigation_id: str):
    return _RESULT_CACHE.get(investigation_id)
