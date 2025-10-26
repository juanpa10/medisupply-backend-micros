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
    
    # Ubicación física en bodega - Requerimiento HU-22
    pasillo = db.Column(db.String(20), nullable=True, index=True)
    estanteria = db.Column(db.String(20), nullable=True, index=True)
    nivel = db.Column(db.String(20), nullable=True, index=True)
    
    # Stock
    cantidad = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # Estado del inventario
    status = db.Column(db.String(20), nullable=False, default=InventoryStatus.AVAILABLE.value)
    
    # Índices compuestos para búsquedas optimizadas
    __table_args__ = (
        Index('idx_location', 'pasillo', 'estanteria', 'nivel'),
    )
    
    def to_dict(self) -> dict:
        """Serializa el item de inventario a diccionario"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'ubicacion': self.get_ubicacion_completa(),
            'pasillo': self.pasillo,
            'estanteria': self.estanteria,
            'nivel': self.nivel,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'status': self.status,
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
        
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<InventoryItem product_id={self.product_id} qty={self.cantidad}>'


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
    
    # Fecha del movimiento
    fecha_movimiento = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Índices para consultas rápidas
    __table_args__ = (
        Index('idx_product_movement', 'product_id', 'fecha_movimiento'),
        Index('idx_item_movement', 'inventory_item_id', 'fecha_movimiento'),
        Index('idx_tipo_fecha', 'tipo', 'fecha_movimiento'),
    )
    
    def to_dict(self) -> dict:
        """Serializa el movimiento a diccionario"""
        return {
            'id': self.id,
            'inventory_item_id': self.inventory_item_id,
            'product_id': self.product_id,
            'tipo': self.tipo,
            'cantidad': float(self.cantidad),
            'cantidad_anterior': float(self.cantidad_anterior) if self.cantidad_anterior else None,
            'cantidad_nueva': float(self.cantidad_nueva) if self.cantidad_nueva else None,
            'motivo': self.motivo,
            'documento_referencia': self.documento_referencia,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'fecha_movimiento': self.fecha_movimiento.isoformat() if self.fecha_movimiento else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<InventoryMovement {self.tipo} product={self.product_id} qty={self.cantidad}>'

