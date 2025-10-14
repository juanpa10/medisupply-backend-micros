"""
Modelo de Proveedor (Supplier)
"""
from app.config.database import db
from app.shared.base_model import BaseModel


class Supplier(BaseModel):
    """
    Modelo de Proveedor
    
    Almacena información completa de proveedores para gestión y comparación
    """
    
    __tablename__ = 'suppliers'
    
    # Campos obligatorios del proveedor
    razon_social = db.Column(db.String(255), nullable=False)
    nit = db.Column(db.String(50), nullable=False, unique=True, index=True)
    representante_legal = db.Column(db.String(255), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    nombre_contacto = db.Column(db.String(255), nullable=False)
    celular_contacto = db.Column(db.String(20), nullable=False)
    
    # Archivo de certificado
    certificado_filename = db.Column(db.String(255), nullable=False)
    certificado_path = db.Column(db.String(500), nullable=False)
    certificado_mime_type = db.Column(db.String(100), nullable=True)
    certificado_size = db.Column(db.Integer, nullable=True)
    
    # Campos opcionales adicionales
    email = db.Column(db.String(255), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(500), nullable=True)
    ciudad = db.Column(db.String(100), nullable=True)
    sitio_web = db.Column(db.String(255), nullable=True)
    notas = db.Column(db.Text, nullable=True)
    
    # Estado del proveedor
    status = db.Column(db.String(20), nullable=False, default='active')
    
    # Índices para búsquedas comunes
    __table_args__ = (
        db.Index('idx_supplier_razon_social', 'razon_social'),
        db.Index('idx_supplier_pais', 'pais'),
        db.Index('idx_supplier_status', 'status'),
    )
    
    def __repr__(self):
        return f'<Supplier {self.razon_social} - {self.nit}>'
    
    def to_dict(self, include_deleted_info=False):
        """
        Convierte el modelo a diccionario
        
        Args:
            include_deleted_info: Si incluir info de eliminación
            
        Returns:
            dict: Representación del proveedor
        """
        data = {
            'id': self.id,
            'razon_social': self.razon_social,
            'nit': self.nit,
            'representante_legal': self.representante_legal,
            'pais': self.pais,
            'nombre_contacto': self.nombre_contacto,
            'celular_contacto': self.celular_contacto,
            'certificado_filename': self.certificado_filename,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'sitio_web': self.sitio_web,
            'notas': self.notas,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
        }
        
        if include_deleted_info:
            data.update({
                'is_deleted': self.is_deleted,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
                'deleted_by': self.deleted_by,
            })
        
        return data
