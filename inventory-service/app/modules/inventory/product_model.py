"""
Modelo Product - Solo para consultas (READ-ONLY)

Este modelo mapea la tabla 'products' que existe en la base de datos compartida.
El inventory-service NO debe modificar esta tabla, solo consultarla.

La gestión de productos (CRUD) es responsabilidad del products-service.
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime, ForeignKey
from app.config.database import db


class Product(db.Model):
    """
    Modelo Product (READ-ONLY)
    
    Este modelo mapea la tabla products para permitir búsquedas
    desde el inventory-service sin necesidad de llamadas HTTP.
    
    IMPORTANTE: Este servicio NO debe crear, actualizar o eliminar productos.
    Solo se usa para consultas y JOINs.
    """
    
    __tablename__ = 'products'
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Información del producto (READ-ONLY)
    nombre = Column(String(200), nullable=False, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    referencia = Column(String(100), index=True)
    descripcion = Column(Text)
    
    # Categorización (Foreign Keys)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), index=True)
    unidad_medida_id = Column(Integer, ForeignKey('unidades_medida.id'), index=True)
    
    # Información del proveedor (Foreign Key)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), index=True)
    
    # Precios base
    precio_compra = Column(Numeric(10, 2))
    precio_venta = Column(Numeric(10, 2))
    
    # Estado
    status = Column(String(20), default='active')
    
    # Auditoría (solo lectura)
    created_at = Column(DateTime)
    created_by = Column(String(100))
    updated_at = Column(DateTime)
    updated_by = Column(String(100))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(100))
    
    def to_dict(self):
        """
        Convierte el producto a diccionario
        Solo campos de lectura
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'referencia': self.referencia,
            'descripcion': self.descripcion,
            'categoria_id': self.categoria_id,
            'unidad_medida_id': self.unidad_medida_id,
            'proveedor_id': self.proveedor_id,
            'precio_compra': str(self.precio_compra) if self.precio_compra else None,
            'precio_venta': str(self.precio_venta) if self.precio_venta else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f"<Product {self.codigo} - {self.nombre}>"
