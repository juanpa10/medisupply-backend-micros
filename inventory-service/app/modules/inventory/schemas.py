"""
Esquemas de validación para el módulo de inventario
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from datetime import date
from app.shared.enums import InventoryStatus, MovementType


class InventoryItemCreateSchema(Schema):
    """Esquema para crear un item de inventario"""
    
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    bodega_id = fields.Int(required=True, validate=validate.Range(min=1))
    bodega_nombre = fields.Str(allow_none=True, validate=validate.Length(max=100))
    
    # Ubicación en bodega
    pasillo = fields.Str(allow_none=True, validate=validate.Length(max=20))
    estanteria = fields.Str(allow_none=True, validate=validate.Length(max=20))
    nivel = fields.Str(allow_none=True, validate=validate.Length(max=20))
    
    # Lote
    lote = fields.Str(allow_none=True, validate=validate.Length(max=50))
    fecha_vencimiento = fields.Date(allow_none=True)
    
    # Stock
    cantidad = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0))
    cantidad_reservada = fields.Decimal(missing=0, as_string=True, validate=validate.Range(min=0))
    cantidad_minima = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))
    cantidad_maxima = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))
    
    # Estado
    status = fields.Str(
        missing=InventoryStatus.AVAILABLE.value,
        validate=validate.OneOf([e.value for e in InventoryStatus])
    )
    
    # Costo
    costo_almacenamiento = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))
    
    @validates_schema
    def validate_ubicacion(self, data, **kwargs):
        """Valida que la ubicación esté completa o vacía"""
        pasillo = data.get('pasillo')
        estanteria = data.get('estanteria')
        nivel = data.get('nivel')
        
        campos_ubicacion = [pasillo, estanteria, nivel]
        campos_completos = sum(1 for campo in campos_ubicacion if campo)
        
        if campos_completos > 0 and campos_completos < 3:
            raise ValidationError(
                'La ubicación debe estar completa (pasillo, estantería y nivel) o vacía',
                field_name='ubicacion'
            )
    
    @validates_schema
    def validate_cantidades(self, data, **kwargs):
        """Valida rangos de cantidad"""
        minima = data.get('cantidad_minima')
        maxima = data.get('cantidad_maxima')
        cantidad = data.get('cantidad', 0)
        reservada = data.get('cantidad_reservada', 0)
        
        if minima is not None and maxima is not None:
            if float(minima) > float(maxima):
                raise ValidationError(
                    'La cantidad mínima no puede ser mayor que la cantidad máxima',
                    field_name='cantidad_minima'
                )
        
        if float(reservada) > float(cantidad):
            raise ValidationError(
                'La cantidad reservada no puede ser mayor que la cantidad total',
                field_name='cantidad_reservada'
            )


class InventoryItemUpdateSchema(Schema):
    """Esquema para actualizar un item de inventario"""
    
    bodega_nombre = fields.Str(allow_none=True, validate=validate.Length(max=100))
    
    # Ubicación
    pasillo = fields.Str(allow_none=True, validate=validate.Length(max=20))
    estanteria = fields.Str(allow_none=True, validate=validate.Length(max=20))
    nivel = fields.Str(allow_none=True, validate=validate.Length(max=20))
    
    # Lote
    lote = fields.Str(allow_none=True, validate=validate.Length(max=50))
    fecha_vencimiento = fields.Date(allow_none=True)
    
    # Stock
    cantidad_minima = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))
    cantidad_maxima = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))
    
    # Estado
    status = fields.Str(validate=validate.OneOf([e.value for e in InventoryStatus]))
    
    # Costo
    costo_almacenamiento = fields.Decimal(allow_none=True, as_string=True, validate=validate.Range(min=0))


class InventorySearchSchema(Schema):
    """Esquema para búsqueda de inventario"""
    
    product_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    bodega_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    lote = fields.Str(allow_none=True, validate=validate.Length(max=50))
    status = fields.Str(allow_none=True, validate=validate.OneOf([e.value for e in InventoryStatus]))
    pasillo = fields.Str(allow_none=True, validate=validate.Length(max=20))
    estanteria = fields.Str(allow_none=True, validate=validate.Length(max=20))
    nivel = fields.Str(allow_none=True, validate=validate.Length(max=20))
    stock_bajo = fields.Bool(allow_none=True)
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))


class InventoryLocationUpdateSchema(Schema):
    """Esquema para actualizar ubicación de un item"""
    
    pasillo = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    estanteria = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    nivel = fields.Str(required=True, validate=validate.Length(min=1, max=20))


class InventoryAdjustmentSchema(Schema):
    """Esquema para ajuste de cantidad (entrada/salida)"""
    
    cantidad = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0.01))
    tipo = fields.Str(required=True, validate=validate.OneOf([e.value for e in MovementType]))
    motivo = fields.Str(allow_none=True, validate=validate.Length(max=200))
    documento_referencia = fields.Str(allow_none=True, validate=validate.Length(max=100))
    usuario_id = fields.Int(allow_none=True)
    usuario_nombre = fields.Str(allow_none=True, validate=validate.Length(max=200))


class InventoryReservationSchema(Schema):
    """Esquema para reservar stock"""
    
    cantidad = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0.01))
    motivo = fields.Str(allow_none=True, validate=validate.Length(max=200))
    documento_referencia = fields.Str(allow_none=True, validate=validate.Length(max=100))


class MovementCreateSchema(Schema):
    """Esquema para crear un movimiento de inventario"""
    
    inventory_item_id = fields.Int(required=True, validate=validate.Range(min=1))
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    bodega_id = fields.Int(required=True, validate=validate.Range(min=1))
    tipo = fields.Str(required=True, validate=validate.OneOf([e.value for e in MovementType]))
    cantidad = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=0.01))
    cantidad_anterior = fields.Decimal(allow_none=True, as_string=True)
    cantidad_nueva = fields.Decimal(allow_none=True, as_string=True)
    motivo = fields.Str(allow_none=True, validate=validate.Length(max=200))
    documento_referencia = fields.Str(allow_none=True, validate=validate.Length(max=100))
    usuario_id = fields.Int(allow_none=True)
    usuario_nombre = fields.Str(allow_none=True, validate=validate.Length(max=200))
    lote = fields.Str(allow_none=True, validate=validate.Length(max=50))


class MovementSearchSchema(Schema):
    """Esquema para búsqueda de movimientos"""
    
    product_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    bodega_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    inventory_item_id = fields.Int(allow_none=True, validate=validate.Range(min=1))
    tipo = fields.Str(allow_none=True, validate=validate.OneOf([e.value for e in MovementType]))
    fecha_desde = fields.Date(allow_none=True)
    fecha_hasta = fields.Date(allow_none=True)
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
