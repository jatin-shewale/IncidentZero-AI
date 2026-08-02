from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.core.database import init_db
from app.core.websocket import manager

from app.api.routes import auth, investigations, agents, chat, reports, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"\n{'='*60}")
    print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"  Mode: {'DEMO' if settings.DEMO_MODE else 'PRODUCTION'}")
    print(f"  Elasticsearch: {'ENABLED (' + settings.ELASTIC_URL + ')' if settings.ELASTIC_ENABLED else 'disabled — using local CSV data engine'}")
    print(f"  Gemma (Ollama): {'ENABLED (' + settings.GEMMA_MODEL + ')' if settings.GEMMA_ENABLED else 'disabled — using deterministic reasoning fallback'}")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(investigations.router)
app.include_router(agents.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "online", "docs": "/docs"}


@app.get("/api/health")
def health():
    from app.gemma.client import is_online as gemma_online
    from app.elastic.client import ping as elastic_ping
    return {
        "status": "ok",
        "demo_mode": settings.DEMO_MODE,
        "gemma_online": gemma_online(),
        "elastic_online": elastic_ping() if settings.ELASTIC_ENABLED else None,
    }


@app.websocket("/ws/investigation/{investigation_id}")
async def ws_investigation(websocket: WebSocket, investigation_id: str):
    await manager.connect(investigation_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive / ignore client pings
    except WebSocketDisconnect:
        manager.disconnect(investigation_id, websocket)
