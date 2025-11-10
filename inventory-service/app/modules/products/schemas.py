"""
Esquemas de validación con Marshmallow para Productos

Incluye validaciones para:
- Creación de productos con archivos
- Actualización de productos
- Validaciones de archivos adjuntos
"""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from werkzeug.datastructures import FileStorage


class ProductCreateSchema(Schema):
    """Esquema para crear un producto"""
    
    # Campos obligatorios
    nombre = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=200, error="El nombre debe tener entre 2 y 200 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9\s\-\.\(\)]+$', error="El nombre contiene caracteres no válidos")
        ],
        error_messages={
            'required': 'El nombre del producto es obligatorio',
            'invalid': 'El nombre debe ser texto'
        }
    )
    
    codigo = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="El código debe tener entre 3 y 50 caracteres"),
            validate.Regexp(r'^[A-Z0-9\-]+$', error="El código solo puede contener letras mayúsculas, números y guiones")
        ],
        error_messages={
            'required': 'El código del producto es obligatorio',
            'invalid': 'El código debe ser texto'
        }
    )
    
    descripcion = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000, error="La descripción debe tener entre 10 y 1000 caracteres"),
        error_messages={
            'required': 'La descripción del producto es obligatoria',
            'invalid': 'La descripción debe ser texto'
        }
    )
    
    categoria_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de categoría debe ser mayor a 0"),
        error_messages={
            'required': 'La categoría es obligatoria',
            'invalid': 'El ID de categoría debe ser un número entero'
        }
    )
    
    unidad_medida_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de unidad de medida debe ser mayor a 0"),
        error_messages={
            'required': 'La unidad de medida es obligatoria',
            'invalid': 'El ID de unidad de medida debe ser un número entero'
        }
    )
    
    proveedor_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de proveedor debe ser mayor a 0"),
        error_messages={
            'required': 'El proveedor es obligatorio',
            'invalid': 'El ID de proveedor debe ser un número entero'
        }
    )
    
    # Campos opcionales
    referencia = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100, error="La referencia no puede exceder 100 caracteres")
    )
    
    precio_compra = fields.Decimal(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, error="El precio de compra debe ser mayor o igual a 0"),
        places=2
    )
    
    precio_venta = fields.Decimal(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, error="El precio de venta debe ser mayor o igual a 0"),
        places=2
    )
    
    # Flags para documentos requeridos
    requiere_ficha_tecnica = fields.Bool(missing=True)
    requiere_condiciones_almacenamiento = fields.Bool(missing=True)
    requiere_certificaciones_sanitarias = fields.Bool(missing=True)
    
    @validates_schema
    def validate_prices(self, data, **kwargs):
        """Validar que el precio de venta sea mayor al de compra si ambos están presentes"""
        precio_compra = data.get('precio_compra')
        precio_venta = data.get('precio_venta')
        
        if precio_compra and precio_venta and precio_venta < precio_compra:
            raise ValidationError('El precio de venta no puede ser menor al precio de compra')


class ProductUpdateSchema(Schema):
    """Esquema para actualizar un producto"""
    
    nombre = fields.Str(
        required=False,
        validate=[
            validate.Length(min=2, max=200, error="El nombre debe tener entre 2 y 200 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9\s\-\.\(\)]+$', error="El nombre contiene caracteres no válidos")
        ]
    )
    
    codigo = fields.Str(
        required=False,
        validate=[
            validate.Length(min=3, max=50, error="El código debe tener entre 3 y 50 caracteres"),
            validate.Regexp(r'^[A-Z0-9\-]+$', error="El código solo puede contener letras mayúsculas, números y guiones")
        ]
    )
    
    descripcion = fields.Str(
        required=False,
        validate=validate.Length(min=10, max=1000, error="La descripción debe tener entre 10 y 1000 caracteres")
    )
    
    categoria_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="El ID de categoría debe ser mayor a 0")
    )
    
    unidad_medida_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="El ID de unidad de medida debe ser mayor a 0")
    )
    
    proveedor_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="El ID de proveedor debe ser mayor a 0")
    )
    
    referencia = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100, error="La referencia no puede exceder 100 caracteres")
    )
    
    precio_compra = fields.Decimal(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, error="El precio de compra debe ser mayor o igual a 0"),
        places=2
    )
    
    precio_venta = fields.Decimal(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, error="El precio de venta debe ser mayor o igual a 0"),
        places=2
    )
    
    status = fields.Str(
        required=False,
        validate=validate.OneOf(['active', 'inactive', 'discontinued'], error="Estado no válido")
    )
    
    requiere_ficha_tecnica = fields.Bool(required=False)
    requiere_condiciones_almacenamiento = fields.Bool(required=False)
    requiere_certificaciones_sanitarias = fields.Bool(required=False)


class ProductFileUploadSchema(Schema):
    """Esquema para validar archivos subidos"""
    
    file_category = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['technical_sheet', 'storage_conditions', 'health_certifications'],
            error="Categoría de archivo no válida"
        ),
        error_messages={
            'required': 'La categoría del archivo es obligatoria'
        }
    )
    
    description = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500, error="La descripción no puede exceder 500 caracteres")
    )
    
    @validates('file')
    def validate_file(self, value):
        """Validar archivo subido"""
        if not value:
            raise ValidationError('Debe proporcionar un archivo')
            
        if not isinstance(value, FileStorage):
            raise ValidationError('El archivo no tiene el formato correcto')
            
        if not value.filename:
            raise ValidationError('El archivo debe tener un nombre')
        
        # Validar extensión
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = '.' + value.filename.rsplit('.', 1)[-1].lower() if '.' in value.filename else ''
        
        if file_ext not in allowed_extensions:
            raise ValidationError(f'Extensión de archivo no permitida. Permitidas: {", ".join(allowed_extensions)}')
        
        # Validar tamaño (5MB máximo)
        if value.content_length and value.content_length > 5 * 1024 * 1024:
            raise ValidationError('El archivo no puede exceder 5MB')


class ProductResponseSchema(Schema):
    """Esquema para respuesta de producto"""
    
    id = fields.Int()
    nombre = fields.Str()
    codigo = fields.Str()
    referencia = fields.Str()
    descripcion = fields.Str()
    categoria_id = fields.Int()
    unidad_medida_id = fields.Int()
    proveedor_id = fields.Int()
    precio_compra = fields.Str()
    precio_venta = fields.Str()
    status = fields.Str()
    requiere_ficha_tecnica = fields.Bool()
    requiere_condiciones_almacenamiento = fields.Bool()
    requiere_certificaciones_sanitarias = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    # Información de relaciones (opcional)
    categoria = fields.Nested({
        'id': fields.Int(),
        'nombre': fields.Str()
    }, required=False)
    
    unidad_medida = fields.Nested({
        'id': fields.Int(),
        'nombre': fields.Str(),
        'abreviatura': fields.Str()
    }, required=False)
    
    proveedor = fields.Nested({
        'id': fields.Int(),
        'nombre': fields.Str()
    }, required=False)
    
    # Archivos (opcional)
    files = fields.List(fields.Nested({
        'id': fields.Int(),
        'file_category': fields.Str(),
        'original_filename': fields.Str(),
        'file_size_bytes': fields.Int(),
        'description': fields.Str(),
        'created_at': fields.DateTime()
    }), required=False)


class ProductListSchema(Schema):
    """Esquema para lista de productos"""
    
    id = fields.Int()
    nombre = fields.Str()
    codigo = fields.Str()
    referencia = fields.Str()
    status = fields.Str()
    categoria_id = fields.Int()
    proveedor_id = fields.Int()
    precio_venta = fields.Str()
    created_at = fields.DateTime()


class ProductSearchSchema(Schema):
    """Esquema para búsqueda de productos"""
    
    q = fields.Str(
        required=False,
        validate=validate.Length(min=2, max=100, error="El término de búsqueda debe tener entre 2 y 100 caracteres")
    )
    
    categoria_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="El ID de categoría debe ser mayor a 0")
    )
    
    proveedor_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="El ID de proveedor debe ser mayor a 0")
    )
    
    status = fields.Str(
        required=False,
        validate=validate.OneOf(['active', 'inactive', 'discontinued', 'all'], error="Estado no válido")
    )
    
    page = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="La página debe ser mayor a 0"),
        missing=1
    )
    
    per_page = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=100, error="Elementos por página debe estar entre 1 y 100"),
        missing=20
    )


# Esquemas para gestión de categorías, unidades y proveedores
class CategoriaCreateSchema(Schema):
    """Esquema para crear categoría"""
    
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100, error="El nombre debe tener entre 2 y 100 caracteres"),
        error_messages={'required': 'El nombre de la categoría es obligatorio'}
    )
    
    descripcion = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500, error="La descripción no puede exceder 500 caracteres")
    )


class UnidadMedidaCreateSchema(Schema):
    """Esquema para crear unidad de medida"""
    
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50, error="El nombre debe tener entre 2 y 50 caracteres"),
        error_messages={'required': 'El nombre de la unidad es obligatorio'}
    )
    
    abreviatura = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=10, error="La abreviatura debe tener entre 1 y 10 caracteres"),
        error_messages={'required': 'La abreviatura es obligatoria'}
    )
    
    descripcion = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500, error="La descripción no puede exceder 500 caracteres")
    )


class ProveedorCreateSchema(Schema):
    """Esquema para crear proveedor"""
    
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200, error="El nombre debe tener entre 2 y 200 caracteres"),
        error_messages={'required': 'El nombre del proveedor es obligatorio'}
    )
    
    nit = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50, error="El NIT no puede exceder 50 caracteres")
    )
    
    contacto_nombre = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100, error="El nombre de contacto no puede exceder 100 caracteres")
    )
    
    contacto_telefono = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=20, error="El teléfono no puede exceder 20 caracteres")
    )
    
    contacto_email = fields.Email(
        required=False,
        allow_none=True,
        error="Email no válido"
    )
    
    direccion = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500, error="La dirección no puede exceder 500 caracteres")
    )
    
    pais = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50, error="El país no puede exceder 50 caracteres")
    )


class ProductBulkUploadSchema(Schema):
    """Esquema para carga masiva de productos desde CSV"""
    
    # Campos obligatorios para cada fila del CSV
    nombre = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=200, error="El nombre debe tener entre 2 y 200 caracteres"),
        ],
        error_messages={'required': 'El nombre es obligatorio'}
    )
    
    codigo = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="El código debe tener entre 3 y 50 caracteres"),
            validate.Regexp(r'^[A-Z0-9\-]+$', error="El código solo puede contener letras mayúsculas, números y guiones")
        ],
        error_messages={'required': 'El código es obligatorio'}
    )
    
    descripcion = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=1000, error="La descripción debe tener entre 5 y 1000 caracteres"),
        error_messages={'required': 'La descripción es obligatoria'}
    )
    
    categoria_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de categoría debe ser mayor a 0"),
        error_messages={'required': 'La categoría es obligatoria'}
    )
    
    unidad_medida_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de unidad de medida debe ser mayor a 0"),
        error_messages={'required': 'La unidad de medida es obligatoria'}
    )
    
    proveedor_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="El ID de proveedor debe ser mayor a 0"),
        error_messages={'required': 'El proveedor es obligatorio'}
    )
    
    # Campos opcionales
    referencia = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100, error="La referencia no puede exceder 100 caracteres")
    )
    
    precio_compra = fields.Decimal(
        required=False,
        allow_none=True,
        places=2,
        validate=validate.Range(min=0, error="El precio de compra debe ser mayor o igual a 0")
    )
    
    precio_venta = fields.Decimal(
        required=False,
        allow_none=True,
        places=2,
        validate=validate.Range(min=0, error="El precio de venta debe ser mayor o igual a 0")
    )
    
    requiere_ficha_tecnica = fields.Bool(
        required=False,
        missing=False,
        error="Debe ser verdadero o falso"
    )
    
    requiere_condiciones_almacenamiento = fields.Bool(
        required=False,
        missing=False,
        error="Debe ser verdadero o falso"
    )
    
    requiere_certificaciones_sanitarias = fields.Bool(
        required=False,
        missing=False,
        error="Debe ser verdadero o falso"
    )