"""
Rutas/Blueprint para el módulo de productos

Define todos los endpoints REST para gestión de productos,
categorías, unidades de medida y proveedores.
"""
from flask import Blueprint
from app.modules.products.controller import (
    ProductController, CategoriaController, UnidadMedidaController, ProveedorController
)
from app.core.auth import require_auth

# Crear blueprint principal
products_bp = Blueprint('products', __name__, url_prefix='/api/v1')

# Inicializar controladores
product_controller = ProductController()
categoria_controller = CategoriaController()
unidad_controller = UnidadMedidaController()
proveedor_controller = ProveedorController()


# ========== RUTAS DE PRODUCTOS ==========

@products_bp.route('/products', methods=['POST'])
@require_auth
def create_product():
    """
    Crear un nuevo producto con archivos opcionales
    
    Content-Type: multipart/form-data
    
    Form fields:
    - nombre (required): Nombre del producto
    - codigo (required): Código único del producto
    - descripcion (required): Descripción del producto
    - categoria_id (required): ID de la categoría
    - unidad_medida_id (required): ID de la unidad de medida
    - proveedor_id (required): ID del proveedor
    - referencia (optional): Referencia del producto
    - precio_compra (optional): Precio de compra
    - precio_venta (optional): Precio de venta
    - requiere_ficha_tecnica (optional): true/false
    - requiere_condiciones_almacenamiento (optional): true/false
    - requiere_certificaciones_sanitarias (optional): true/false
    
    Files:
    - technical_sheet (optional): Ficha técnica
    - storage_conditions (optional): Condiciones de almacenamiento
    - health_certifications (optional): Certificaciones sanitarias
    """
    return product_controller.create_product()


@products_bp.route('/products/<int:product_id>', methods=['GET'])
@require_auth
def get_product(product_id):
    """
    Obtener un producto por ID
    
    Incluye información de relaciones y archivos adjuntos.
    """
    return product_controller.get_product(product_id)


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_auth
def update_product(product_id):
    """
    Actualizar un producto
    
    Content-Type: application/json o multipart/form-data
    """
    return product_controller.update_product(product_id)


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@require_auth
def delete_product(product_id):
    """
    Eliminar un producto (soft delete)
    """
    return product_controller.delete_product(product_id)


@products_bp.route('/products', methods=['GET'])
@require_auth
def get_products():
    """
    Listar productos con paginación
    
    Query params:
    - page: Número de página (default: 1)
    - per_page: Elementos por página (default: 20, max: 100)
    """
    return product_controller.get_products()


@products_bp.route('/products/search', methods=['GET'])
@require_auth
def search_products():
    """
    Buscar productos con filtros
    
    Query params:
    - q: Término de búsqueda (nombre, código, referencia, descripción)
    - categoria_id: Filtro por categoría
    - proveedor_id: Filtro por proveedor
    - status: Filtro por estado (active, inactive, discontinued, all)
    - page: Número de página (default: 1)
    - per_page: Elementos por página (default: 20, max: 100)
    """
    return product_controller.search_products()


# ========== RUTAS DE ARCHIVOS DE PRODUCTOS ==========

@products_bp.route('/products/<int:product_id>/files', methods=['POST'])
@require_auth
def add_product_file(product_id):
    """
    Agregar un archivo a un producto
    
    Content-Type: multipart/form-data
    
    Form fields:
    - file_category (required): technical_sheet, storage_conditions, health_certifications
    - description (optional): Descripción del archivo
    
    Files:
    - file (required): Archivo a subir
    """
    return product_controller.add_product_file(product_id)


@products_bp.route('/products/<int:product_id>/files', methods=['GET'])
@require_auth
def get_product_files(product_id):
    """
    Obtener archivos de un producto
    
    Query params:
    - file_category (optional): Filtrar por categoría de archivo
    """
    return product_controller.get_product_files(product_id)


@products_bp.route('/products/files/<int:file_id>', methods=['DELETE'])
@require_auth
def delete_product_file(file_id):
    """
    Eliminar un archivo de producto
    """
    return product_controller.delete_product_file(file_id)


@products_bp.route('/products/files/<int:file_id>/download', methods=['GET'])
@require_auth
def download_product_file(file_id):
    """
    Descargar un archivo de producto
    """
    return product_controller.download_product_file(file_id)


# ========== RUTAS DE ESTADO DEL CATÁLOGO ==========

@products_bp.route('/products/<int:product_id>/catalog-status', methods=['GET'])
@require_auth
def get_product_catalog_status(product_id):
    """
    Obtener estado del producto en el catálogo
    
    Incluye información sobre documentos requeridos y disponibilidad.
    """
    return product_controller.get_product_catalog_status(product_id)


@products_bp.route('/products/missing-documents', methods=['GET'])
@require_auth
def get_products_missing_documents():
    """
    Obtener productos que no tienen documentos requeridos
    """
    return product_controller.get_products_missing_documents()


# ========== RUTAS DE CATEGORÍAS ==========

@products_bp.route('/categorias', methods=['POST'])
@require_auth
def create_categoria():
    """
    Crear una nueva categoría
    
    Content-Type: application/json
    
    Body:
    {
        "nombre": "Nombre de la categoría",
        "descripcion": "Descripción opcional"
    }
    """
    return categoria_controller.create_categoria()


@products_bp.route('/categorias', methods=['GET'])
@require_auth
def get_categorias():
    """
    Obtener todas las categorías activas
    """
    return categoria_controller.get_categorias()


# ========== RUTAS DE UNIDADES DE MEDIDA ==========

@products_bp.route('/unidades-medida', methods=['POST'])
@require_auth
def create_unidad_medida():
    """
    Crear una nueva unidad de medida
    
    Content-Type: application/json
    
    Body:
    {
        "nombre": "Nombre de la unidad",
        "abreviatura": "Abreviatura única",
        "descripcion": "Descripción opcional"
    }
    """
    return unidad_controller.create_unidad_medida()


@products_bp.route('/unidades-medida', methods=['GET'])
@require_auth
def get_unidades_medida():
    """
    Obtener todas las unidades de medida activas
    """
    return unidad_controller.get_unidades_medida()


# ========== RUTAS DE PROVEEDORES ==========

@products_bp.route('/proveedores', methods=['POST'])
@require_auth
def create_proveedor():
    """
    Crear un nuevo proveedor
    
    Content-Type: application/json
    
    Body:
    {
        "nombre": "Nombre del proveedor",
        "nit": "NIT opcional",
        "contacto_nombre": "Nombre de contacto",
        "contacto_telefono": "Teléfono",
        "contacto_email": "email@ejemplo.com",
        "direccion": "Dirección",
        "pais": "País"
    }
    """
    return proveedor_controller.create_proveedor()


@products_bp.route('/proveedores', methods=['GET'])
@require_auth
def get_proveedores():
    """
    Obtener proveedores
    
    Query params:
    - q (optional): Término de búsqueda por nombre o NIT
    """
    return proveedor_controller.get_proveedores()


# ========== DOCUMENTACIÓN DE ENDPOINTS ==========

@products_bp.route('/products/docs', methods=['GET'])
def get_products_docs():
    """
    Documentación de endpoints de productos
    """
    endpoints = {
        "productos": {
            "POST /api/v1/products": "Crear producto con archivos",
            "GET /api/v1/products": "Listar productos",
            "GET /api/v1/products/search": "Buscar productos",
            "GET /api/v1/products/{id}": "Obtener producto",
            "PUT /api/v1/products/{id}": "Actualizar producto",
            "DELETE /api/v1/products/{id}": "Eliminar producto"
        },
        "archivos": {
            "POST /api/v1/products/{id}/files": "Agregar archivo",
            "GET /api/v1/products/{id}/files": "Listar archivos",
            "DELETE /api/v1/products/files/{file_id}": "Eliminar archivo",
            "GET /api/v1/products/files/{file_id}/download": "Descargar archivo"
        },
        "catálogo": {
            "GET /api/v1/products/{id}/catalog-status": "Estado en catálogo",
            "GET /api/v1/products/missing-documents": "Productos sin documentos"
        },
        "maestros": {
            "POST /api/v1/categorias": "Crear categoría",
            "GET /api/v1/categorias": "Listar categorías",
            "POST /api/v1/unidades-medida": "Crear unidad de medida",
            "GET /api/v1/unidades-medida": "Listar unidades",
            "POST /api/v1/proveedores": "Crear proveedor",
            "GET /api/v1/proveedores": "Listar proveedores"
        }
    }
    
    from app.core.utils.response import success_response
    return success_response(
        data=endpoints,
        message="Documentación de endpoints de productos"
    )