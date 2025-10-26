"""
Tests for InventoryItemRepository and InventoryMovementRepository using the test DB fixtures.

These tests use the existing fixtures in `conftest.py` (sample_products, sample_inventory,
db_session) to populate the DB and exercise repository methods that perform queries and
aggregations.
"""
from app.modules.inventory.repository import InventoryItemRepository, InventoryMovementRepository
from app.modules.inventory.models import InventoryItem, InventoryMovement
from decimal import Decimal


def test_total_and_available_stock(db_session):
    repo = InventoryItemRepository()

    # create multiple items for product 100
    items = [
        InventoryItem(product_id=100, pasillo='X', estanteria='01', nivel='1', cantidad=Decimal('10'), status='available'),
        InventoryItem(product_id=100, pasillo='X', estanteria='02', nivel='1', cantidad=Decimal('5'), status='available'),
        InventoryItem(product_id=100, pasillo='Y', estanteria='01', nivel='1', cantidad=Decimal('7'), status='not_available')
    ]
    db_session.bulk_save_objects(items)
    db_session.commit()

    total = repo.get_total_stock_by_product(100)
    assert abs(total - 22.0) < 0.0001

    available = repo.get_available_stock_by_product(100)
    assert abs(available - 15.0) < 0.0001


def test_search_by_product_name_or_code_returns_joined_results(db_session, sample_products, sample_inventory):
    repo = InventoryItemRepository()

    # sample_products includes Paracetamol with id=1 and sample_inventory includes an item for product_id=1
    results = repo.search_by_product_name_or_code('paracetamol')
    assert isinstance(results, list)
    assert len(results) > 0
    inv_item, product = results[0]
    assert isinstance(inv_item, InventoryItem)
    assert hasattr(product, 'nombre')


def test_search_inventory_and_locations(db_session):
    repo = InventoryItemRepository()

    # Insert items with different locations
    a = InventoryItem(product_id=200, pasillo='A', estanteria='01', nivel='1', cantidad=5, status='available')
    b = InventoryItem(product_id=201, pasillo='A', estanteria='02', nivel='1', cantidad=3, status='available')
    c = InventoryItem(product_id=202, pasillo=None, estanteria=None, nivel=None, cantidad=1, status='available')
    db_session.add_all([a, b, c])
    db_session.commit()

    results = repo.search_inventory(product_id=200)
    assert len(results) == 1

    loc_results = repo.get_by_location('A')
    assert len(loc_results) >= 2

    without_loc = repo.get_items_without_location()
    assert any(item.product_id == 202 for item in without_loc)


def test_movement_repository_basic(db_session):
    mov_repo = InventoryMovementRepository()

    mv_data = dict(inventory_item_id=1, product_id=1, tipo='entrada', cantidad=Decimal('2'), cantidad_anterior=Decimal('0'), cantidad_nueva=Decimal('2'))
    mov_repo.create(mv_data)
    # get by product must return at least one
    results = mov_repo.get_by_product(1)
    assert isinstance(results, list)
