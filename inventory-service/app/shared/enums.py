"""
Enumeraciones compartidas del Inventory Service
"""
from enum import Enum


class InventoryStatus(str, Enum):
    """Estado del item de inventario"""
    AVAILABLE = 'available'  # Disponible para uso
    RESERVED = 'reserved'  # Reservado para una orden
    QUARANTINE = 'quarantine'  # En cuarentena (revisión de calidad)
    DAMAGED = 'damaged'  # Dañado
    EXPIRED = 'expired'  # Vencido
    IN_TRANSIT = 'in_transit'  # En tránsito


class MovementType(str, Enum):
    """Tipo de movimiento de inventario"""
    ENTRADA = 'entrada'  # Entrada de stock (compras, devoluciones)
    SALIDA = 'salida'  # Salida de stock (ventas, consumo)
    AJUSTE = 'ajuste'  # Ajuste manual de inventario
    TRANSFERENCIA = 'transferencia'  # Transferencia entre bodegas
    DEVOLUCION_CLIENTE = 'devolucion_cliente'  # Devolución de cliente
    DEVOLUCION_PROVEEDOR = 'devolucion_proveedor'  # Devolución a proveedor
    MERMA = 'merma'  # Pérdida por deterioro, vencimiento, etc.


class MeasurementUnit(str, Enum):
    """Unidad de medida (heredada para compatibilidad)"""
    UNIT = 'unit'
    BOX = 'box'
    PACKAGE = 'package'
    KG = 'kg'
    LITER = 'liter'

