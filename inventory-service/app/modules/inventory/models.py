"""
Modelos de Inventario - Stock y ubicación en bodega
"""
from datetime import datetime
from sqlalchemy import Index, ForeignKey
from app.config.database import db
from app.shared.base_model import BaseModel
from app.shared.enums import InventoryStatus, MovementType


class InventoryItem(BaseModel):
    """
    Modelo de Item de Inventario
    
    Almacena el stock y ubicación de un producto en bodega.
    Los datos del producto (nombre, descripción, etc.) están en products-service.
    
    Responsabilidades:
    - Stock actual y alertas (min/max)
    - Ubicación física en bodega (pasillo, estantería, nivel)
    - Lotes y fechas de vencimiento
    - Bodega/almacén donde se encuentra
    
    Optimizado para búsquedas rápidas (< 1 segundo) por product_id, lote o ubicación.
    """
    
    __tablename__ = 'inventory_items'
    
    # Relación con microservicio de productos
    product_id = db.Column(db.Integer, nullable=False, index=True)  # ID del producto en products-service
    
    # Bodega/Almacén
    bodega_id = db.Column(db.Integer, nullable=False, index=True, default=1)  # ID de la bodega
    bodega_nombre = db.Column(db.String(100), nullable=True)  # Nombre descriptivo de la bodega
    
    # Ubicación física en bodega - Requerimiento HU-22
    pasillo = db.Column(db.String(20), nullable=True, index=True)
    estanteria = db.Column(db.String(20), nullable=True, index=True)
    nivel = db.Column(db.String(20), nullable=True, index=True)
    
    # Información de lote
    lote = db.Column(db.String(50), nullable=True, index=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True, index=True)
    
    # Stock
    cantidad = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad_reservada = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Cantidad comprometida en órdenes
    cantidad_disponible = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # cantidad - cantidad_reservada
    
    # Alertas de stock
    cantidad_minima = db.Column(db.Numeric(10, 2), nullable=True)
    cantidad_maxima = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Estado del inventario
    status = db.Column(db.String(20), nullable=False, default=InventoryStatus.AVAILABLE.value)
    
    # Costo de almacenamiento (diferente al precio base del catálogo)
    costo_almacenamiento = db.Column(db.Numeric(10, 2), nullable=True)  # Costo mensual de mantener el stock
    
    # Índices compuestos para búsquedas optimizadas
    __table_args__ = (
        Index('idx_product_bodega', 'product_id', 'bodega_id'),
        Index('idx_location', 'bodega_id', 'pasillo', 'estanteria', 'nivel'),
        Index('idx_product_lote', 'product_id', 'lote'),
        Index('idx_vencimiento', 'fecha_vencimiento'),
        Index('idx_stock_bajo', 'cantidad', 'cantidad_minima'),
    )
    
    def to_dict(self) -> dict:
        """Serializa el item de inventario a diccionario"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'bodega_id': self.bodega_id,
            'bodega_nombre': self.bodega_nombre,
            'ubicacion': self.get_ubicacion_completa(),
            'pasillo': self.pasillo,
            'estanteria': self.estanteria,
            'nivel': self.nivel,
            'lote': self.lote,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'cantidad_reservada': float(self.cantidad_reservada) if self.cantidad_reservada else 0,
            'cantidad_disponible': float(self.cantidad_disponible) if self.cantidad_disponible else 0,
            'cantidad_minima': float(self.cantidad_minima) if self.cantidad_minima else None,
            'cantidad_maxima': float(self.cantidad_maxima) if self.cantidad_maxima else None,
            'status': self.status,
            'costo_almacenamiento': float(self.costo_almacenamiento) if self.costo_almacenamiento else None,
            'alerta_stock': self.get_alerta_stock(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_ubicacion_completa(self) -> str:
        """Retorna la ubicación completa en formato legible"""
        if not self.tiene_ubicacion():
            return "Sin ubicación asignada"
        
        partes = []
        if self.pasillo:
            partes.append(f"Pasillo {self.pasillo}")
        if self.estanteria:
            partes.append(f"Estantería {self.estanteria}")
        if self.nivel:
            partes.append(f"Nivel {self.nivel}")
        
        return " - ".join(partes) if partes else "Ubicación parcial"
    
    def tiene_ubicacion(self) -> bool:
        """Verifica si el item tiene ubicación asignada"""
        return bool(self.pasillo or self.estanteria or self.nivel)
    
    def is_stock_bajo(self) -> bool:
        """Verifica si el stock está por debajo del mínimo"""
        if self.cantidad_minima is None:
            return False
        return self.cantidad_disponible < self.cantidad_minima
    
    def is_stock_alto(self) -> bool:
        """Verifica si el stock está por encima del máximo"""
        if self.cantidad_maxima is None:
            return False
        return self.cantidad > self.cantidad_maxima
    
    def get_alerta_stock(self) -> str:
        """Retorna el estado de alerta de stock"""
        if self.is_stock_bajo():
            return "stock_bajo"
        elif self.is_stock_alto():
            return "stock_alto"
        return "normal"
    
    def actualizar_ubicacion(self, pasillo: str = None, estanteria: str = None, nivel: str = None):
        """Actualiza la ubicación del item en bodega"""
        if pasillo is not None:
            self.pasillo = pasillo
        if estanteria is not None:
            self.estanteria = estanteria
        if nivel is not None:
            self.nivel = nivel
        self.updated_at = datetime.utcnow()
    
    def ajustar_cantidad(self, cantidad_cambio: float, es_entrada: bool = True):
        """
        Ajusta la cantidad del item
        
        Args:
            cantidad_cambio: Cantidad a agregar o quitar
            es_entrada: True para entrada (suma), False para salida (resta)
        """
        if es_entrada:
            self.cantidad += cantidad_cambio
        else:
            self.cantidad -= cantidad_cambio
        
        # Recalcular disponible
        self.cantidad_disponible = self.cantidad - self.cantidad_reservada
        self.updated_at = datetime.utcnow()
    
    def reservar_stock(self, cantidad_a_reservar: float) -> bool:
        """
        Reserva stock para una orden
        
        Returns:
            True si se pudo reservar, False si no hay suficiente disponible
        """
        if self.cantidad_disponible >= cantidad_a_reservar:
            self.cantidad_reservada += cantidad_a_reservar
            self.cantidad_disponible = self.cantidad - self.cantidad_reservada
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def liberar_stock(self, cantidad_a_liberar: float):
        """Libera stock reservado"""
        self.cantidad_reservada = max(0, self.cantidad_reservada - cantidad_a_liberar)
        self.cantidad_disponible = self.cantidad - self.cantidad_reservada
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<InventoryItem product_id={self.product_id} bodega={self.bodega_id} qty={self.cantidad}>'


class InventoryMovement(BaseModel):
    """
    Modelo de Movimiento de Inventario
    
    Registra todas las entradas y salidas de inventario.
    Permite trazabilidad completa de movimientos de stock.
    """
    
    __tablename__ = 'inventory_movements'
    
    # Relación con el item de inventario
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False, index=True)
    
    # Información del producto (desnormalizado para consultas rápidas)
    product_id = db.Column(db.Integer, nullable=False, index=True)
    bodega_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Tipo de movimiento
    tipo = db.Column(db.String(30), nullable=False, index=True)  # entrada, salida, ajuste, transferencia
    
    # Cantidad y detalles
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad_anterior = db.Column(db.Numeric(10, 2), nullable=True)
    cantidad_nueva = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Motivo y referencia
    motivo = db.Column(db.String(200), nullable=True)
    documento_referencia = db.Column(db.String(100), nullable=True, index=True)  # Ej: factura, orden de compra
    
    # Usuario que realizó el movimiento
    usuario_id = db.Column(db.Integer, nullable=True, index=True)
    usuario_nombre = db.Column(db.String(200), nullable=True)
    
    # Lote (si aplica)
    lote = db.Column(db.String(50), nullable=True, index=True)
    
    # Fecha del movimiento
    fecha_movimiento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Índices para consultas rápidas
    __table_args__ = (
        Index('idx_product_movement', 'product_id', 'fecha_movimiento'),
        Index('idx_item_movement', 'inventory_item_id', 'fecha_movimiento'),
        Index('idx_tipo_fecha', 'tipo', 'fecha_movimiento'),
        Index('idx_bodega_fecha', 'bodega_id', 'fecha_movimiento'),
    )
    
    def to_dict(self) -> dict:
        """Serializa el movimiento a diccionario"""
        return {
            'id': self.id,
            'inventory_item_id': self.inventory_item_id,
            'product_id': self.product_id,
            'bodega_id': self.bodega_id,
            'tipo': self.tipo,
            'cantidad': float(self.cantidad),
            'cantidad_anterior': float(self.cantidad_anterior) if self.cantidad_anterior else None,
            'cantidad_nueva': float(self.cantidad_nueva) if self.cantidad_nueva else None,
            'motivo': self.motivo,
            'documento_referencia': self.documento_referencia,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'lote': self.lote,
            'fecha_movimiento': self.fecha_movimiento.isoformat() if self.fecha_movimiento else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<InventoryMovement {self.tipo} product={self.product_id} qty={self.cantidad}>'

