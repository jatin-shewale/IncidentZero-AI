import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.incident import Investigation
from app.data_engine.local_store import local_store

_counter = {"n": 44}


def _next_id() -> str:
    _counter["n"] += 1
    return f"INC-2026-{_counter['n']:03d}"


def _extract_host(query: str) -> str:
    """Pull a hostname out of a free-text query, defaulting to the first
    host in inventory if none is mentioned (keeps the API usable for any
    natural-language phrasing, per the spec's 'natural language investigation
    request' requirement)."""
    hosts = [h["hostname"] for h in local_store.hosts()]
    for h in hosts:
        if h.lower() in query.lower():
            return h
    match = re.search(r"\b([A-Z]{2,}-[A-Z0-9]+-\d+)\b", query.upper())
    if match and match.group(1) in hosts:
        return match.group(1)
    return hosts[0] if hosts else "UNKNOWN-HOST"


def create_investigation(db: Session, query: str, host: str = None) -> Investigation:
    inv_id = _next_id()
    target_host = host or _extract_host(query)
    inv = Investigation(
        id=inv_id,
        title=query.strip()[:120] or f"Investigation of {target_host}",
        query=query,
        host=target_host,
        status="queued",
        severity="info",
        risk_score=0,
        confidence=0,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def get_investigation(db: Session, investigation_id: str) -> Investigation:
    return db.query(Investigation).filter(Investigation.id == investigation_id).first()


def list_investigations(db: Session):
    return db.query(Investigation).order_by(Investigation.created_at.desc()).all()
