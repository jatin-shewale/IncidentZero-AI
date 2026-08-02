from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import asyncio

from app.core.database import get_db, SessionLocal
from app.schemas.incident_schema import CreateInvestigationRequest, InvestigationOut
from app.services import investigation_service
from app.agents.orchestrator import run_investigation, get_cached_result

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


@router.post("/create")
def create(payload: CreateInvestigationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    inv = investigation_service.create_investigation(db, payload.query, payload.host)
    inv_id, host, query = inv.id, inv.host, payload.query

    def _run():
        # Background tasks run after the request's DB session closes, so we
        # open a fresh session scoped to just this investigation run.
        bg_db = SessionLocal()
        try:
            asyncio.run(run_investigation(bg_db, inv_id, query, host))
        finally:
            bg_db.close()

    background_tasks.add_task(_run)
    return {"investigation_id": inv.id, "host": inv.host, "status": "started"}


@router.get("")
def list_all(db: Session = Depends(get_db)):
    rows = investigation_service.list_investigations(db)
    return [
        {
            "id": r.id, "title": r.title, "host": r.host, "risk_score": r.risk_score,
            "confidence": r.confidence, "status": r.status, "severity": r.severity,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/{investigation_id}")
def get_one(investigation_id: str, db: Session = Depends(get_db)):
    inv = investigation_service.get_investigation(db, investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return {
        "id": inv.id, "title": inv.title, "host": inv.host, "risk_score": inv.risk_score,
        "confidence": inv.confidence, "status": inv.status, "severity": inv.severity,
        "summary": inv.summary,
    }


@router.get("/{investigation_id}/timeline")
def timeline(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return []
    return result["timeline"]


@router.get("/{investigation_id}/graph")
def graph(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return {"nodes": [], "edges": []}
    return result["graph"]


@router.get("/{investigation_id}/evidence")
def evidence(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return []
    return result["findings"]


@router.get("/{investigation_id}/iocs")
def iocs(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return []
    return result["iocs"]


@router.get("/{investigation_id}/mitre")
def mitre(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return []
    return result["mitre"]


@router.get("/{investigation_id}/response")
def response_plan(investigation_id: str):
    result = get_cached_result(investigation_id)
    if not result:
        return {"immediate_actions": [], "long_term": []}
    return result["response"]
