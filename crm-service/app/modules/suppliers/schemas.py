"""
Esquemas de validación con Marshmallow para Suppliers
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.shared.enums import Country
from app.core.utils.validators import validate_nit, validate_phone


class SupplierCreateSchema(Schema):
    """Esquema para crear un proveedor"""
    
    razon_social = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'La razón social es obligatoria'}
    )
    
    nit = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=50),
        error_messages={'required': 'El NIT es obligatorio'}
    )
    
    representante_legal = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'El representante legal es obligatorio'}
    )
    
    pais = fields.Str(
        required=True,
        validate=validate.OneOf(Country.list()),
        error_messages={'required': 'El país es obligatorio'}
    )
    
    nombre_contacto = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={'required': 'El nombre del contacto es obligatorio'}
    )
    
    celular_contacto = fields.Str(
        required=True,
        validate=validate.Length(min=7, max=20),
        error_messages={'required': 'El celular de contacto es obligatorio'}
    )
    
    # Campos opcionales
    email = fields.Email(required=False, allow_none=True)
    telefono = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    direccion = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    ciudad = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    sitio_web = fields.Url(required=False, allow_none=True)
    notas = fields.Str(required=False, allow_none=True)
    
    @validates('nit')
    def validate_nit_format(self, value):
        """Valida el formato del NIT"""
        try:
            validate_nit(value)
        except Exception as e:
            raise ValidationError(str(e))
    
    @validates('celular_contacto')
    def validate_phone_format(self, value):
        """Valida el formato del teléfono"""
        try:
            validate_phone(value)
        except Exception as e:
            raise ValidationError(str(e))


class SupplierUpdateSchema(Schema):
    """Esquema para actualizar un proveedor"""
    
    razon_social = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=255)
    )
    
    representante_legal = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=255)
    )
    
    pais = fields.Str(
        required=False,
        validate=validate.OneOf(Country.list())
    )
    
    nombre_contacto = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=255)
    )
    
    celular_contacto = fields.Str(
        required=False,
        validate=validate.Length(min=7, max=20)
    )
    
    email = fields.Email(required=False, allow_none=True)
    telefono = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    direccion = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    ciudad = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    sitio_web = fields.Url(required=False, allow_none=True)
    notas = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=False, validate=validate.OneOf(['active', 'inactive']))


class SupplierResponseSchema(Schema):
    """Esquema para respuesta de proveedor"""
    
    id = fields.Int()
    razon_social = fields.Str()
    nit = fields.Str()
    representante_legal = fields.Str()
    pais = fields.Str()
    nombre_contacto = fields.Str()
    celular_contacto = fields.Str()
    certificado_filename = fields.Str()
    email = fields.Str(allow_none=True)
    telefono = fields.Str(allow_none=True)
    direccion = fields.Str(allow_none=True)
    ciudad = fields.Str(allow_none=True)
    sitio_web = fields.Str(allow_none=True)
    notas = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime()
    created_by = fields.Str(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)
    updated_by = fields.Str(allow_none=True)


class SupplierListSchema(Schema):
    """Esquema para lista de proveedores"""
    
    id = fields.Int()
    razon_social = fields.Str()
    nit = fields.Str()
    pais = fields.Str()
    nombre_contacto = fields.Str()
    celular_contacto = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
