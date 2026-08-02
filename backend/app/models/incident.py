from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True, index=True)  # e.g. INC-2026-045
    title = Column(String, nullable=False)
    query = Column(Text, nullable=True)
    host = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    risk_score = Column(Float, default=0)
    confidence = Column(Float, default=0)
    status = Column(String, default="queued")  # queued | investigating | investigating_complete | failed
    severity = Column(String, default="info")  # info | warn | crit
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    executions = relationship("AgentExecution", back_populates="investigation", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String, ForeignKey("investigations.id"))
    agent_name = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending | running | done | error
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    time_taken_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="executions")
