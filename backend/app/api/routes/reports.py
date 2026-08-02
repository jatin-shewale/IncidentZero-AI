from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.services.report_service import build_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate/{investigation_id}")
def generate(investigation_id: str, kind: str = "technical"):
    content = build_report(investigation_id, kind)
    return {"investigation_id": investigation_id, "kind": kind, "content": content}


@router.get("/generate/{investigation_id}/download", response_class=PlainTextResponse)
def download(investigation_id: str, kind: str = "technical"):
    content = build_report(investigation_id, kind)
    return PlainTextResponse(content, media_type="text/markdown")
