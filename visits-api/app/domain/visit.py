from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class VisitStatus:
    PLANNED = "planned"; IN_PROGRESS = "in_progress"; FINISHED = "finished"; RESCHEDULED = "rescheduled"
class VisitResult:
    SUCCESS = "success"; RESCHEDULED = "rescheduled"; FAILED = "failed"

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    commercial_id = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stops = relationship("VisitStop", back_populates="visit", cascade="all, delete-orphan")

class VisitStop(Base):
    __tablename__ = "visit_stops"
    id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    position = Column(Integer, nullable=False)
    status = Column(String, default=VisitStatus.PLANNED, nullable=False)
    checkin_at = Column(DateTime, nullable=True); checkout_at = Column(DateTime, nullable=True)
    lat = Column(String, nullable=True); lon = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    result = Column(String, nullable=True); result_reason = Column(String, nullable=True)
    notes = Column(String, nullable=True); tags = Column(String, nullable=True)
    visit = relationship("Visit", back_populates="stops")
