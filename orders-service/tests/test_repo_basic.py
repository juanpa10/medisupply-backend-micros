import os
from app.db import Base, engine, SessionLocal
from app.repositories.repo import Repo
from app.domain.models import Order, OrderStatusHistory


def setup_module(module):
    # ensure fresh DB for these unit tests
    db_path = engine.url.database
    if db_path and os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_get_list_update():
    repo = Repo()
    # Create
    o = repo.create_order('cust-x', 'UT-0001', 'pendiente')
    assert o.order_number == 'UT-0001'
    # Get
    got = repo.get_order_by_number('UT-0001')
    assert got is not None and got.customer_id == 'cust-x'
    # List
    arr = repo.list_orders_for_customer('cust-x')
    assert any(x.order_number == 'UT-0001' for x in arr)
    # Update status and ensure history created
    o2 = repo.update_order_status('UT-0001', 'transito', note='test')
    assert o2.status == 'transito'
    # History exists
    s = repo.session
    hist = s.query(OrderStatusHistory).filter_by(order_id=o2.id).all()
    assert len(hist) >= 1
