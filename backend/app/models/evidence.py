from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(String, ForeignKey("investigations.id"))
    source = Column(String, nullable=False)       # e.g. Sysmon, DNS Logs, Network Logs
    event = Column(String, nullable=False)        # short title
    severity = Column(String, default="medium")   # low | medium | high | critical
    explanation = Column(Text, nullable=True)      # why it matters
    confidence = Column(Float, default=0)
    raw_event = Column(Text, nullable=True)        # JSON-encoded raw source record
    timestamp = Column(DateTime, default=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="evidence")
