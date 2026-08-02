from fastapi import APIRouter
from app.agents.orchestrator import PIPELINE_STEPS
from app.gemma.client import is_online as gemma_online
from app.config.settings import settings

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/status")
def status():
    return {
        "gemma_online": gemma_online(),
        "gemma_model": settings.GEMMA_MODEL,
        "elastic_enabled": settings.ELASTIC_ENABLED,
        "demo_mode": settings.DEMO_MODE,
        "agents": [{"name": name, "status": "idle"} for name in PIPELINE_STEPS],
    }
