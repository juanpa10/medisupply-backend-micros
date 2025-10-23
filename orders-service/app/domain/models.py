from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, text
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db import Base


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    order_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    # Allowed statuses (exact strings used by clients)
    # case enPreparacion = "En preparacion"
    # case transito = "transito"
    # case entregado = "entregado"
    # case pendiente = "pendiente"
    ALLOWED_STATUSES = ("En preparacion", "transito", "entregado", "pendiente")
    status: Mapped[str] = mapped_column(String, nullable=False, default='pendiente')
    # Provide Python-side defaults to avoid RETURNING/server-default race on SQLite
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    # allow nullable and set a python default; onupdate keeps timestamps fresh
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    # total amount for the order (monetary value). Stored as float for simplicity (units: whatever callers expect)
    monto: Mapped[float] = mapped_column(type_=String, nullable=False, default='0.0')
    history = relationship('OrderStatusHistory', back_populates='order', cascade='all, delete-orphan')
    # order items relationship
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class OrderStatusHistory(Base):
    __tablename__ = 'order_status_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    previous_status: Mapped[str] = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    note: Mapped[str] = mapped_column(Text, nullable=True)
    order = relationship('Order', back_populates='history')


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    unit_price: Mapped[float] = mapped_column(type_=String, nullable=False, default='0.0')
    # backref to order items
    items = relationship('OrderItem', back_populates='product')


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=True, index=True)
    # snapshot values to keep historical prices
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(type_=String, nullable=False, default='0.0')

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='items')

