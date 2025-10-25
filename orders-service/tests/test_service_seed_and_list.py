import os
from app.db import Base, engine
from app.services.orders_service import OrdersService, svc


def setup_function(func):
    # fresh DB for service tests
    db_path = engine.url.database
    if db_path and os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_seed_creates_defaults():
    service = OrdersService()
    # seed should insert a couple orders when DB empty
    service.seed()
    arr = service.list_orders('cust-1')
    # seed creates at least one order for cust-1
    assert any(o.order_number.startswith('ORD-') for o in arr)
