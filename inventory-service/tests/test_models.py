"""
Tests for InventoryItem and InventoryMovement model helpers.

These tests operate on the SQLAlchemy model classes but don't commit to the
database; they only validate in-memory behavior of helper methods.
"""
from decimal import Decimal
from app.modules.inventory.models import InventoryItem, InventoryMovement
from datetime import datetime


def test_inventory_item_location_helpers():
    item = InventoryItem(
        product_id=1,
        pasillo=None,
        estanteria=None,
        nivel=None,
        cantidad=Decimal('0'),
        status='available'
    )

    # No location
    assert item.tiene_ubicacion() is False
    assert item.get_ubicacion_completa() == 'Sin ubicación asignada'

    # Partial location
    item.pasillo = 'A'
    assert item.tiene_ubicacion() is True
    assert 'Pasillo A' in item.get_ubicacion_completa()

    # Full location
    item.estanteria = '02'
    item.nivel = '1'
    full = item.get_ubicacion_completa()
    assert 'Pasillo A' in full and 'Estantería 02' in full and 'Nivel 1' in full

    # actualizar_ubicacion
    item.actualizar_ubicacion(pasillo='B', estanteria='03', nivel='2')
    assert item.pasillo == 'B'
    assert item.estanteria == '03'
    assert item.nivel == '2'


def test_adjust_quantity_and_to_dict():
    item = InventoryItem(product_id=2, cantidad=Decimal('10'))
    # ajustar entrada
    item.ajustar_cantidad(Decimal('5'), es_entrada=True)
    assert Decimal(item.cantidad) == Decimal('15')

    # ajustar salida
    item.ajustar_cantidad(Decimal('3'), es_entrada=False)
    assert Decimal(item.cantidad) == Decimal('12')

    d = item.to_dict()
    assert d['product_id'] == 2
    assert isinstance(d['cantidad'], float)


def test_inventory_movement_to_dict_and_repr():
    mv = InventoryMovement(
        inventory_item_id=1,
        product_id=2,
        tipo='entrada',
        cantidad=Decimal('5'),
        cantidad_anterior=Decimal('0'),
        cantidad_nueva=Decimal('5'),
        motivo='test',
        documento_referencia='DOC',
        usuario_id=1,
        usuario_nombre='u',
        fecha_movimiento=datetime.utcnow()
    )

    d = mv.to_dict()
    assert d['product_id'] == 2
    assert d['tipo'] == 'entrada'
    assert isinstance(d['cantidad'], float)
    assert 'fecha_movimiento' in d
