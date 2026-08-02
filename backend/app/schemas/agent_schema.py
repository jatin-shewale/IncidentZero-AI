from typing import List, Optional
from pydantic import BaseModel


class AgentStatusOut(BaseModel):
    name: str
    status: str
    last_output: Optional[str] = None


class ChatRequest(BaseModel):
    investigation_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    evidence: List[str] = []


class ReportRequest(BaseModel):
    kind: str = "technical"  # technical | executive
