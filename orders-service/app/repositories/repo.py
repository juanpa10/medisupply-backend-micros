"""Orders repository - single clean implementation."""

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, ProgrammingError, DBAPIError
from app.db import SessionLocal
from app.domain.models import Order, OrderStatusHistory, Product, OrderItem
from app.db import engine
from datetime import datetime


class SimpleOrder:
    """Lightweight order-like object returned when DB schema is missing new columns.
    This avoids raising an exception in production when the database hasn't been migrated yet.
    """
    def __init__(self, id=None, order_number=None, status=None, monto='0.0'):
        self.id = id
        self.order_number = order_number
        self.status = status
        self.monto = monto


class Repo:
    """Repository for orders-service using SQLAlchemy sessions."""
    def __init__(self, session=None):
        self.session = session or SessionLocal()

    def list_orders_for_customer(self, customer_id: str, state: str | None = None, start_date=None, end_date=None):
        """Return list of Order objects for a given customer, optionally filtered by state."""
        q = select(Order).filter_by(customer_id=customer_id)
        if state:
            q = q.filter_by(status=state)
        return self.session.execute(q).scalars().all()

    def get_order_by_number(self, order_number: str):
        """Return single Order by order_number or None."""
        q = select(Order).filter_by(order_number=order_number)
        return self.session.execute(q).scalars().first()

    def create_order(self, customer_id: str, order_number: str, status: str = 'pendiente', items: list | None = None):
        """Create and return a new Order. Items is a list of dicts with keys:
        - product_id (optional) OR name + unit_price
        - quantity (optional, defaults to 1)
        - unit_price (optional if product_id provided)
        The function will create Product entries if name/unit_price provided and compute monto.
        """
        o = Order(customer_id=customer_id, order_number=order_number, status=status)
        self.session.add(o)

        # compute total from items (try to resolve product prices from current session when possible)
        total = 0.0
        try:
            if items:
                # make lightweight product creations/lookups; flush later to persist order id
                for it in items:
                    qty = int(it.get('quantity', 1))
                    product = None
                    unit_price = None
                    if 'product_id' in it and it.get('product_id') is not None:
                        product = self.session.get(Product, int(it['product_id']))
                        if product:
                            unit_price = float(product.unit_price)
                    if product is None and 'name' in it and 'unit_price' in it:
                        product = Product(name=it['name'], description=it.get('description'), unit_price=str(float(it['unit_price'])))
                        self.session.add(product)
                        # flush product so it has an id
                        self.session.flush()
                        unit_price = float(product.unit_price)
                    if unit_price is None and 'unit_price' in it:
                        unit_price = float(it['unit_price'])
                    if unit_price is None:
                        unit_price = 0.0
                    total += qty * unit_price

            # attempt to flush and commit normally (may raise ProgrammingError if DB missing 'monto')
            o.monto = str(float(total))
            self.session.add(o)
            self.session.flush()

            # now create order items referencing o.id
            if items:
                for it in items:
                    qty = int(it.get('quantity', 1))
                    # try to use product already in session by name/id
                    product = None
                    if 'product_id' in it and it.get('product_id') is not None:
                        product = self.session.get(Product, int(it['product_id']))
                    else:
                        # try find product by name in session (recently added) or leave None
                        name = it.get('name')
                        product = None
                    unit_price = None
                    if product:
                        unit_price = float(product.unit_price)
                    elif 'unit_price' in it:
                        unit_price = float(it['unit_price'])
                    else:
                        unit_price = 0.0
                    oi = OrderItem(order_id=o.id, product_id=product.id if product else None, product_name=product.name if product else it.get('name', ''), quantity=qty, unit_price=str(unit_price))
                    self.session.add(oi)

            # commit final
            try:
                self.session.commit()
            except IntegrityError:
                try:
                    self.session.rollback()
                except Exception:
                    pass
                raise
            self.session.refresh(o)
            return o

        except ProgrammingError as pe:
            # likely missing 'monto' column in DB schema; fallback to raw INSERT without monto and persist items separately
            try:
                self.session.rollback()
            except Exception:
                pass

            # compute total using a fresh session to resolve any product prices referenced by id
            total = 0.0
            if items:
                s2 = SessionLocal()
                try:
                    for it in items:
                        qty = int(it.get('quantity', 1))
                        unit_price = None
                        if 'product_id' in it and it.get('product_id') is not None:
                            p = s2.get(Product, int(it['product_id']))
                            if p:
                                unit_price = float(p.unit_price)
                        if unit_price is None and 'unit_price' in it:
                            unit_price = float(it['unit_price'])
                        if unit_price is None:
                            unit_price = 0.0
                        total += qty * unit_price
                finally:
                    s2.close()

            # ensure timestamps are not null (DB has NOT NULL constraint)
            created_at_val = o.created_at or datetime.utcnow()
            updated_at_val = o.updated_at or created_at_val
            params = {
                'customer_id': customer_id,
                'order_number': order_number,
                'status': status,
                'created_at': created_at_val,
                'updated_at': updated_at_val,
            }
            # Use a transaction on a fresh connection to avoid mixing with session state
            with engine.begin() as conn:
                try:
                    res = conn.execute(text("INSERT INTO orders (customer_id, order_number, status, created_at, updated_at) VALUES (:customer_id, :order_number, :status, :created_at, :updated_at) RETURNING id"), params)
                    inserted_id = int(res.scalar_one())
                except DBAPIError:
                    conn.execute(text("INSERT INTO orders (customer_id, order_number, status, created_at, updated_at) VALUES (:customer_id, :order_number, :status, :created_at, :updated_at)"), params)
                    r = conn.execute(text("SELECT id FROM orders WHERE order_number = :order_number LIMIT 1"), {'order_number': order_number})
                    row = r.first()
                    inserted_id = int(row[0]) if row is not None else None

            # persist items using fresh session
            s = SessionLocal()
            try:
                for it in items or []:
                    qty = int(it.get('quantity', 1))
                    product = None
                    unit_price = None
                    if 'product_id' in it and it.get('product_id') is not None:
                        product = s.get(Product, int(it['product_id']))
                        if product:
                            unit_price = float(product.unit_price)
                    if product is None and 'name' in it and 'unit_price' in it:
                        product = Product(name=it['name'], description=it.get('description'), unit_price=str(float(it['unit_price'])))
                        s.add(product)
                        s.flush()
                        unit_price = float(product.unit_price)
                    if unit_price is None and 'unit_price' in it:
                        unit_price = float(it['unit_price'])
                    if unit_price is None:
                        unit_price = 0.0
                    oi = OrderItem(order_id=inserted_id, product_id=product.id if product else None, product_name=product.name if product else it.get('name', ''), quantity=qty, unit_price=str(unit_price))
                    s.add(oi)
                s.commit()
            except Exception:
                try:
                    s.rollback()
                except Exception:
                    pass
            finally:
                s.close()

            return SimpleOrder(id=inserted_id, order_number=order_number, status=status, monto=str(float(total)))

    def update_order_status(self, order_number: str, new_status: str, note: str | None = None):
        """Update status for an order and append a history row."""
        o = self.get_order_by_number(order_number)
        if not o:
            return None
        prev = o.status
        o.status = new_status
        self.session.add(o)
        self.session.commit()
        # persist history
        h = OrderStatusHistory(order_id=o.id, previous_status=prev, new_status=new_status, note=note)
        self.session.add(h)
        self.session.commit()
        self.session.refresh(o)
        return o

