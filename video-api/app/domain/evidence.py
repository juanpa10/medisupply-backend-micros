from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from app.db import Base

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    client_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    visit_id = Column(String, nullable=False)
    user = Column(String, nullable=True)   # tomado del token si aplica
    evidence_type = Column(String, nullable=False) # photo | video
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    stored_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed = Column(Boolean, default=True, nullable=False)  # simplificado: true al guardar
