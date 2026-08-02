from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.incident import Investigation

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    rows = db.query(Investigation).all()
    total = len(rows)
    crit = len([r for r in rows if r.severity == "crit"])
    avg_risk = round(sum(r.risk_score for r in rows) / total, 1) if total else 0
    avg_conf = round(sum(r.confidence for r in rows) / total, 1) if total else 0

    by_status = {}
    for r in rows:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    return {
        "total_investigations": total,
        "critical_investigations": crit,
        "avg_risk_score": avg_risk,
        "avg_confidence": avg_conf,
        "by_status": by_status,
        "estimated_time_saved_minutes": total * 43,  # avg. manual investigation ~45min vs ~2min AI-assisted
    }
