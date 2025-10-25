import os
from app.db import Base, engine, SessionLocal
from app.repositories.repo import Repo
from app.domain.models import Product


def setup_module(module):
    # fresh DB for these tests
    db_path = engine.url.database
    if db_path and os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_order_with_inline_products_and_monto():
    repo = Repo()
    payload = [
        {'name': 'Inline A', 'unit_price': 3.5, 'quantity': 3},
        {'name': 'Inline B', 'unit_price': 2.0, 'quantity': 2}
    ]
    o = repo.create_order('cust-items', 'IT-100', items=payload)
    assert o is not None
    # monto = 3.5*3 + 2.0*2 = 10.5 + 4 = 14.5
    assert abs(float(o.monto) - 14.5) < 1e-6
    # products should have been created
    s = repo.session
    prod_count = s.query(Product).count()
    assert prod_count >= 2


def test_create_order_with_existing_product_reference():
    repo = Repo()
    s = repo.session
    # create a product manually
    p = Product(name='Stored X', description='desc', unit_price=str(7.5))
    s.add(p)
    s.commit()
    s.refresh(p)
    # create order referencing product_id
    items = [{'product_id': p.id, 'quantity': 2}]
    o = repo.create_order('cust-items', 'IT-101', items=items)
    assert abs(float(o.monto) - 15.0) < 1e-6


def test_create_order_with_missing_price_defaults_to_zero():
    repo = Repo()
    items = [{'name': 'Freebie', 'quantity': 5}]
    o = repo.create_order('cust-items', 'IT-102', items=items)
    # unit_price missing -> treated as 0.0
    assert abs(float(o.monto) - 0.0) < 1e-6


def test_create_order_with_product_id_lookup():
    repo = Repo()
    s = repo.session
    # create a product and then use its id when creating an order
    p = Product(name='LookupProd', description='x', unit_price=str(4.25))
    s.add(p)
    s.commit()
    s.refresh(p)
    items = [{'product_id': p.id, 'quantity': 3}]
    o = repo.create_order('cust-lookup', 'IT-200', items=items)
    assert abs(float(o.monto) - (3 * 4.25)) < 1e-6


def test_list_orders_filters_by_state():
    repo = Repo()
    repo.create_order('cf', 'F-1', status='pendiente')
    repo.create_order('cf', 'F-2', status='transito')
    arr = repo.list_orders_for_customer('cf', state='transito')
    assert len(arr) == 1 and arr[0].order_number == 'F-2'
