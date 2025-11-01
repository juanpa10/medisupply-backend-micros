from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

ALLOWED_STATUSES = {"alistamiento","despachado","entregado"}

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    delivery_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
