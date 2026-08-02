import re
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.incident import Investigation
from app.data_engine.local_store import local_store

def _next_id() -> str:
    return f"INC-2026-{uuid.uuid4().hex[:8].upper()}"


def _extract_host(query: str) -> str:
    """Pull a hostname out of a free-text query.

    If no host can be matched, return None instead of guessing a default.
    That keeps unknown targets from silently collapsing onto a real host.
    """
    hosts = [h["hostname"] for h in local_store.hosts()]
    normalized_hosts = {re.sub(r"[^a-z0-9]", "", h.lower()): h for h in hosts}
    normalized_query = re.sub(r"[^a-z0-9]", "", query.lower())

    for normalized, host_name in normalized_hosts.items():
        if normalized and normalized in normalized_query:
            return host_name

    for h in hosts:
        if h.lower() in query.lower():
            return h

    match = re.search(r"\b([A-Z]{2,}-[A-Z0-9-]+)\b", query.upper())
    if match:
        candidate = match.group(1)
        if candidate in hosts:
            return candidate

    return None


def create_investigation(db: Session, query: str, host: str = None) -> Investigation:
    inv_id = _next_id()
    target_host = host or _extract_host(query)
    inv = Investigation(
        id=inv_id,
        title=query.strip()[:120] or (f"Investigation of {target_host}" if target_host else "Investigation request"),
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
