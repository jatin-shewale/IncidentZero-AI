import json
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    """Tracks active WebSocket clients per investigation_id and broadcasts events."""

    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, investigation_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(investigation_id, []).append(ws)

    def disconnect(self, investigation_id: str, ws: WebSocket):
        if investigation_id in self.active and ws in self.active[investigation_id]:
            self.active[investigation_id].remove(ws)
            if not self.active[investigation_id]:
                del self.active[investigation_id]

    async def broadcast(self, investigation_id: str, event: dict):
        for ws in list(self.active.get(investigation_id, [])):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                self.disconnect(investigation_id, ws)


manager = ConnectionManager()
