"""
Modelos de productos con gestión de archivos

Incluye:
- Product: Modelo principal de productos (CRUD completo)
- ProductFile: Modelo para gestión de archivos adjuntos
- Categoria, UnidadMedida, Proveedor: Modelos de referencia
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.config.database import db
from app.shared.base_model import BaseModel


class Categoria(BaseModel):
    """
    Modelo de Categoría de Productos
    """
    __tablename__ = 'categorias'
    
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    status = Column(String(20), default='active')
    
    # Relaciones
    products = relationship('Product', back_populates='categoria')
    
    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class UnidadMedida(BaseModel):
    """
    Modelo de Unidad de Medida
    """
    __tablename__ = 'unidades_medida'
    
    nombre = Column(String(50), nullable=False, unique=True)
    abreviatura = Column(String(10), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    status = Column(String(20), default='active')
    
    # Relaciones
    products = relationship('Product', back_populates='unidad_medida')
    
    def __repr__(self):
        return f"<UnidadMedida {self.nombre} ({self.abreviatura})>"


class Proveedor(BaseModel):
    """
    Modelo de Proveedor
    """
    __tablename__ = 'proveedores'
    
    nombre = Column(String(200), nullable=False, index=True)
    nit = Column(String(50), unique=True, nullable=True)
    contacto_nombre = Column(String(100), nullable=True)
    contacto_telefono = Column(String(20), nullable=True)
    contacto_email = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
    pais = Column(String(50), nullable=True)
    status = Column(String(20), default='active')
    
    # Relaciones
    products = relationship('Product', back_populates='proveedor')
    
    def __repr__(self):
        return f"<Proveedor {self.nombre}>"


class Product(BaseModel):
    """
    Modelo Principal de Productos (CRUD Completo)
    
    Gestiona la información completa de productos incluyendo:
    - Datos básicos (nombre, código, descripción)
    - Categorización (categoria, unidad de medida, proveedor)
    - Precios
    - Archivos adjuntos (ficha técnica, condiciones, certificaciones)
    """
    
    __tablename__ = 'products'
    
    # Información básica del producto
    nombre = Column(String(200), nullable=False, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    referencia = Column(String(100), nullable=True, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Categorización (Foreign Keys)
    categoria_id = Column(Integer, ForeignKey('categorias.id'), nullable=False, index=True)
    unidad_medida_id = Column(Integer, ForeignKey('unidades_medida.id'), nullable=False, index=True)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), nullable=False, index=True)
    
    # Precios
    precio_compra = Column(Numeric(10, 2), nullable=True)
    precio_venta = Column(Numeric(10, 2), nullable=True)
    
    # Estado del producto
    status = Column(String(20), default='active')  # active, inactive, discontinued
    
    # Flags para control de documentos requeridos
    requiere_ficha_tecnica = Column(Boolean, default=True)
    requiere_condiciones_almacenamiento = Column(Boolean, default=True)
    requiere_certificaciones_sanitarias = Column(Boolean, default=True)
    
    # Relaciones
    categoria = relationship('Categoria', back_populates='products')
    unidad_medida = relationship('UnidadMedida', back_populates='products')
    proveedor = relationship('Proveedor', back_populates='products')
    files = relationship('ProductFile', back_populates='product', cascade='all, delete-orphan')
    
    # Índices
    __table_args__ = (
        db.Index('idx_product_nombre', 'nombre'),
        db.Index('idx_product_codigo', 'codigo'),
        db.Index('idx_product_status', 'status'),
        db.Index('idx_product_categoria', 'categoria_id'),
    )
    
    def to_dict(self, include_files=False):
        """
        Convierte el producto a diccionario
        """
        result = {
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
            'status': self.status,
            'requiere_ficha_tecnica': self.requiere_ficha_tecnica,
            'requiere_condiciones_almacenamiento': self.requiere_condiciones_almacenamiento,
            'requiere_certificaciones_sanitarias': self.requiere_certificaciones_sanitarias,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Incluir información de relaciones si están cargadas
        if hasattr(self, 'categoria') and self.categoria:
            result['categoria'] = {
                'id': self.categoria.id,
                'nombre': self.categoria.nombre
            }
            
        if hasattr(self, 'unidad_medida') and self.unidad_medida:
            result['unidad_medida'] = {
                'id': self.unidad_medida.id,
                'nombre': self.unidad_medida.nombre,
                'abreviatura': self.unidad_medida.abreviatura
            }
            
        if hasattr(self, 'proveedor') and self.proveedor:
            result['proveedor'] = {
                'id': self.proveedor.id,
                'nombre': self.proveedor.nombre
            }
        
        # Incluir archivos si se solicita
        if include_files and hasattr(self, 'files'):
            result['files'] = [file.to_dict() for file in self.files]
            
        return result
    
    def has_required_documents(self):
        """
        Verifica si el producto tiene todos los documentos requeridos
        """
        required_files = []
        if self.requiere_ficha_tecnica:
            required_files.append('technical_sheet')
        if self.requiere_condiciones_almacenamiento:
            required_files.append('storage_conditions')
        if self.requiere_certificaciones_sanitarias:
            required_files.append('health_certifications')
        
        if not required_files:
            return True
            
        # Verificar que existan archivos activos para cada categoría requerida
        existing_categories = {f.file_category for f in self.files if f.status == 'active'}
        return all(cat in existing_categories for cat in required_files)
    
    def get_catalog_status(self):
        """
        Determina si el producto está disponible en el catálogo
        """
        if self.status != 'active':
            return 'unavailable', 'Producto inactivo'
        
        if not self.has_required_documents():
            return 'pending_documents', 'Faltan documentos requeridos'
            
        return 'available', 'Disponible en catálogo'
    
    def __repr__(self):
        return f"<Product {self.codigo} - {self.nombre}>"


class ProductFile(BaseModel):
    """
    Modelo para gestión de archivos de productos
    
    Categorías de archivos:
    - technical_sheet: Ficha técnica
    - storage_conditions: Condiciones de almacenamiento  
    - health_certifications: Certificaciones sanitarias
    """
    
    __tablename__ = 'product_files'
    
    # Relación con producto
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    
    # Categoría del archivo
    file_category = Column(String(50), nullable=False, index=True)  # technical_sheet, storage_conditions, health_certifications
    
    # Información del archivo
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(Text, nullable=False)
    
    # Metadata
    description = Column(Text, nullable=True)
    status = Column(String(50), default='active')  # active, deleted, archived
    
    # Usuario que subió el archivo
    uploaded_by_user_id = Column(Integer, nullable=True)
    uploaded_by_username = Column(String(100), nullable=True)
    
    # Relaciones
    product = relationship('Product', back_populates='files')
    
    # Índices
    __table_args__ = (
        db.Index('idx_product_file_category', 'product_id', 'file_category'),
        db.Index('idx_product_file_status', 'status'),
    )
    
    def to_dict(self):
        """
        Convierte el archivo a diccionario
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'file_category': self.file_category,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'mime_type': self.mime_type,
            'file_extension': self.file_extension,
            'file_size_bytes': self.file_size_bytes,
            'storage_path': self.storage_path,
            'description': self.description,
            'status': self.status,
            'uploaded_by_user_id': self.uploaded_by_user_id,
            'uploaded_by_username': self.uploaded_by_username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_file_category_display(self):
        """
        Retorna nombre amigable de la categoría del archivo
        """
        categories = {
            'technical_sheet': 'Ficha Técnica',
            'storage_conditions': 'Condiciones de Almacenamiento',
            'health_certifications': 'Certificaciones Sanitarias'
        }
        return categories.get(self.file_category, self.file_category)
    
    def __repr__(self):
        return f"<ProductFile {self.original_filename} ({self.file_category})>"