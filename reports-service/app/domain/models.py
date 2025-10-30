from sqlalchemy import Column, Integer, String, Date, Numeric, Index
from sqlalchemy.orm import relationship
from app.db import Base


class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    salesperson = Column(String(100), index=True, nullable=False)
    product = Column(String(100), index=True, nullable=False)
    zone = Column(String(100), index=True, nullable=False)
    amount = Column(Numeric(12,2), nullable=False)

    __table_args__ = (
        Index('ix_sales_date_salesperson', 'date', 'salesperson'),
        Index('ix_sales_date_product', 'date', 'product'),
        Index('ix_sales_date_zone', 'date', 'zone'),
    )
