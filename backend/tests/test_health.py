"""
Minimal smoke tests. Run with:  pytest backend/tests
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.__enter__()  # trigger lifespan startup so init_db() runs and tables exist


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_run_investigation():
    r = client.post("/api/investigations/create", json={"query": "Investigate suspicious activity on FIN-PC-023"})
    assert r.status_code == 200
    inv_id = r.json()["investigation_id"]
    assert inv_id.startswith("INC-2026-")

    import time
    time.sleep(3)  # background pipeline runs synchronously fast, but give it a beat

    r2 = client.get(f"/api/investigations/{inv_id}")
    assert r2.status_code == 200
    body = r2.json()
    assert body["host"] == "FIN-PC-023"


def test_mcp_tools_import():
    from app.mcp_layer.server import mcp
    assert mcp.name == "IncidentZero-Security-Tools"


def test_agents_status():
    r = client.get("/api/agents/status")
    assert r.status_code == 200
    assert "agents" in r.json()
