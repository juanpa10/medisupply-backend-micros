"""
Unit tests for InventoryService business logic.

These tests avoid touching the DB by mocking the repositories used by the
service. They exercise validation and movement registration logic.
"""
from types import SimpleNamespace
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.modules.inventory.service import InventoryService
from app.core.exceptions import ValidationError, BusinessError, ResourceNotFoundError
from app.shared.enums import MovementType


def make_fake_item(**kwargs):
    # Provide default attributes used by the service
    defaults = dict(
        id=kwargs.get('id', 1),
        product_id=kwargs.get('product_id', 1),
        bodega_id=kwargs.get('bodega_id', 1),
        pasillo=kwargs.get('pasillo', 'A'),
        estanteria=kwargs.get('estanteria', '01'),
        nivel=kwargs.get('nivel', '1'),
        cantidad=kwargs.get('cantidad', Decimal('0')),
        cantidad_disponible=kwargs.get('cantidad_disponible', Decimal('0')),
        cantidad_reservada=kwargs.get('cantidad_reservada', Decimal('0')),
        lote=kwargs.get('lote', None),
    )

    obj = SimpleNamespace()
    # set attributes from defaults
    for k, v in defaults.items():
        setattr(obj, k, v)

    # simple methods used by service that mutate the object
    def ajustar_cantidad(cambio, es_entrada=True):
        if es_entrada:
            obj.cantidad = Decimal(obj.cantidad) + Decimal(cambio)
            obj.cantidad_disponible = Decimal(obj.cantidad_disponible) + Decimal(cambio)
        else:
            obj.cantidad = Decimal(obj.cantidad) - Decimal(cambio)
            obj.cantidad_disponible = Decimal(obj.cantidad_disponible) - Decimal(cambio)

    def reservar_stock(cantidad):
        cantidad = Decimal(cantidad)
        if Decimal(obj.cantidad_disponible) >= cantidad:
            obj.cantidad_reservada = Decimal(getattr(obj, 'cantidad_reservada', 0)) + cantidad
            obj.cantidad_disponible = Decimal(obj.cantidad_disponible) - cantidad
            return True
        return False

    def liberar_stock(cantidad):
        cantidad = Decimal(cantidad)
        obj.cantidad_reservada = max(Decimal(getattr(obj, 'cantidad_reservada', 0)) - cantidad, Decimal(0))
        obj.cantidad_disponible = Decimal(getattr(obj, 'cantidad_disponible', 0)) + cantidad

    def actualizar_ubicacion(pasillo=None, estanteria=None, nivel=None):
        if pasillo is not None:
            obj.pasillo = pasillo
        if estanteria is not None:
            obj.estanteria = estanteria
        if nivel is not None:
            obj.nivel = nivel

    obj.ajustar_cantidad = ajustar_cantidad
    obj.reservar_stock = reservar_stock
    obj.liberar_stock = liberar_stock
    obj.actualizar_ubicacion = actualizar_ubicacion

    return obj


@pytest.fixture(autouse=True)
def disable_db_commit(monkeypatch):
    """Patch the db object used in the service module to avoid needing an app context."""
    fake_db = SimpleNamespace()
    fake_db.session = SimpleNamespace(commit=lambda: None)
    monkeypatch.setattr('app.modules.inventory.service.db', fake_db)
    # Patch InventoryMovement in the service module so tests don't construct the SQLAlchemy model
    class _FakeMovement(SimpleNamespace):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    monkeypatch.setattr('app.modules.inventory.service.InventoryMovement', _FakeMovement)
    yield


def test_create_inventory_item_when_exists_raises_validation_error():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    svc.repo.get_by_product_and_bodega.return_value = True

    data = {'product_id': 1, 'bodega_id': 2, 'cantidad': 10}

    with pytest.raises(ValidationError):
        svc.create_inventory_item(data)


def test_create_inventory_item_registers_movement_and_sets_disponible():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    # No existing item
    svc.repo.get_by_product_and_bodega.return_value = None

    # When repo.create is called, set an id on the passed item (simulate DB)
    def create_side_effect(instance):
        # ensure attribute assignment works even if instance is a SimpleNamespace
        try:
            instance.id = 42
        except Exception:
            setattr(instance, 'id', 42)
        return instance

    svc.repo.create.side_effect = create_side_effect

    data = {
        'product_id': 10,
        'bodega_id': 5,
        'cantidad': 15,
        'usuario_id': 7,
        'usuario_nombre': 'tester'
    }

    # Patch the InventoryItem class used inside the service so it accepts arbitrary kwargs
    from unittest.mock import patch
    from types import SimpleNamespace

    class FakeInventoryItem(SimpleNamespace):
        def __init__(self, **kwargs):
            # provide defaults for attributes the service expects
            kwargs.setdefault('lote', None)
            kwargs.setdefault('cantidad_disponible', Decimal('0'))
            kwargs.setdefault('cantidad_reservada', Decimal('0'))
            super().__init__(**kwargs)

    class FakeInventoryMovement(SimpleNamespace):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    with patch('app.modules.inventory.service.InventoryItem', new=FakeInventoryItem), \
         patch('app.modules.inventory.service.InventoryMovement', new=FakeInventoryMovement):
        item = svc.create_inventory_item(data)

    # repo.create should have been called with an InventoryItem-like instance
    assert svc.repo.create.call_count == 1

    # item should have cantidad_disponible computed
    assert float(item.cantidad_disponible) == float(Decimal('15') - Decimal('0'))

    # movement_repo.create should have been called once for the initial entrada
    assert svc.movement_repo.create.call_count == 1


def test_adjust_stock_entry_and_exit_and_insufficient():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    # Entry case
    item = make_fake_item(id=1, cantidad=Decimal('10'), cantidad_disponible=Decimal('10'))
    svc.repo.get_by_id.return_value = item

    updated = svc.adjust_stock(item_id=1, cantidad=Decimal('5'), tipo=MovementType.ENTRADA.value)
    assert Decimal(updated.cantidad) == Decimal('15')
    assert svc.movement_repo.create.call_count == 1

    # Exit case with enough stock
    svc.movement_repo.create.reset_mock()
    item = make_fake_item(id=2, cantidad=Decimal('10'), cantidad_disponible=Decimal('8'))
    svc.repo.get_by_id.return_value = item

    updated = svc.adjust_stock(item_id=2, cantidad=Decimal('3'), tipo='salida')
    assert Decimal(updated.cantidad) == Decimal('7')
    assert svc.movement_repo.create.call_count == 1

    # Exit case insufficient stock
    item = make_fake_item(id=3, cantidad=Decimal('2'), cantidad_disponible=Decimal('1'))
    svc.repo.get_by_id.return_value = item

    with pytest.raises(BusinessError):
        svc.adjust_stock(item_id=3, cantidad=Decimal('5'), tipo='salida')


def test_reserve_and_release_stock_behaviour():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    # Reserve success
    item = make_fake_item(id=5, cantidad=Decimal('20'), cantidad_disponible=Decimal('20'))
    svc.repo.get_by_id.return_value = item

    updated = svc.reserve_stock(item_id=5, cantidad=Decimal('5'), motivo='test')
    assert Decimal(updated.cantidad_reservada) == Decimal('5')

    # Reserve failure
    item2 = make_fake_item(id=6, cantidad=Decimal('3'), cantidad_disponible=Decimal('1'))
    svc.repo.get_by_id.return_value = item2

    with pytest.raises(BusinessError):
        svc.reserve_stock(item_id=6, cantidad=Decimal('2'))

    # Release
    item3 = make_fake_item(id=7, cantidad=Decimal('10'), cantidad_disponible=Decimal('2'), cantidad_reservada=Decimal('3'))
    svc.repo.get_by_id.return_value = item3

    released = svc.release_stock(item_id=7, cantidad=Decimal('2'))
    assert Decimal(released.cantidad_reservada) == Decimal('1')


def test_update_location_and_search_query_validation():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    # update_location happy path
    item = make_fake_item(id=9)
    svc.repo.get_by_id.return_value = item

    updated = svc.update_location(item_id=9, pasillo='Z', estanteria='99', nivel='3')
    assert updated.pasillo == 'Z'
    assert updated.estanteria == '99'
    assert updated.nivel == '3'

    # search_by_product_query validation
    with pytest.raises(ValidationError):
        svc.search_by_product_query('a')


def test__register_movement_creates_movement_with_expected_fields():
    svc = InventoryService()
    svc.repo = MagicMock()
    svc.movement_repo = MagicMock()

    item = make_fake_item(id=12, product_id=77, bodega_id=8, cantidad=Decimal('100'))

    movement = svc._register_movement(
        item=item,
        tipo=MovementType.ENTRADA.value,
        cantidad=Decimal('5'),
        cantidad_anterior=Decimal('95'),
        cantidad_nueva=Decimal('100'),
        motivo='unit test',
        documento_referencia='DOC-1',
        usuario_id=1,
        usuario_nombre='u'
    )

    # movement_repo.create should be invoked
    assert svc.movement_repo.create.call_count == 1
    # returned object should have product_id and inventory_item_id set
    assert movement.product_id == 77
    assert movement.inventory_item_id == 12
