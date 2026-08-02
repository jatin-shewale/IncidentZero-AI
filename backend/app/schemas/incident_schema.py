from typing import List, Optional
from pydantic import BaseModel


class CreateInvestigationRequest(BaseModel):
    query: str
    host: Optional[str] = None


class InvestigationOut(BaseModel):
    id: str
    title: str
    host: Optional[str] = None
    risk_score: float
    confidence: float
    status: str
    severity: str
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class EvidenceOut(BaseModel):
    id: int
    source: str
    event: str
    severity: str
    explanation: Optional[str]
    confidence: float
    timestamp: str

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    time: str
    event: str
    source: str
    severity: str
    details: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class AttackGraphOut(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class MitreFinding(BaseModel):
    technique_id: str
    name: str
    tactic: str
    confidence: float
    evidence: str


class ResponsePlan(BaseModel):
    immediate_actions: List[str]
    long_term: List[str]
