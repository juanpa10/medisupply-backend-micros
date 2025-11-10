"""
Controladores REST para gestión de productos

Endpoints para:
- CRUD de productos con archivos
- Gestión de categorías, unidades y proveedores
- Búsqueda y filtros
"""
from typing import Dict, Any
from flask import request, g, send_file, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from app.modules.products.service import ProductService, CategoriaService, UnidadMedidaService, ProveedorService
from app.modules.products.schemas import (
    ProductCreateSchema, ProductUpdateSchema, ProductFileUploadSchema,
    ProductResponseSchema, ProductListSchema, ProductSearchSchema,
    CategoriaCreateSchema, UnidadMedidaCreateSchema, ProveedorCreateSchema
)
from app.core.utils.response import success_response, error_response, paginated_response
from app.core.exceptions import ValidationError as AppValidationError, ConflictError, BusinessError, ResourceNotFoundError
from app.core.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)


class ProductController:
    """Controlador para endpoints de productos"""
    
    def __init__(self):
        self.service = ProductService()
        self.create_schema = ProductCreateSchema()
        self.update_schema = ProductUpdateSchema()
        self.response_schema = ProductResponseSchema()
        self.list_schema = ProductListSchema()
        self.search_schema = ProductSearchSchema()
    
    def create_product(self):
        """
        POST /api/v1/products
        
        Crea un nuevo producto con archivos opcionales (multipart/form-data)
        """
        try:
            # Obtener usuario actual
            current_user = getattr(g, 'username', 'system')
            
            # Validar datos del formulario
            form_data = request.form.to_dict()
            
            # Convertir strings a tipos apropiados
            if 'categoria_id' in form_data:
                form_data['categoria_id'] = int(form_data['categoria_id'])
            if 'unidad_medida_id' in form_data:
                form_data['unidad_medida_id'] = int(form_data['unidad_medida_id'])
            if 'proveedor_id' in form_data:
                form_data['proveedor_id'] = int(form_data['proveedor_id'])
            if 'precio_compra' in form_data and form_data['precio_compra']:
                form_data['precio_compra'] = float(form_data['precio_compra'])
            if 'precio_venta' in form_data and form_data['precio_venta']:
                form_data['precio_venta'] = float(form_data['precio_venta'])
            
            # Convertir flags booleanos
            for flag in ['requiere_ficha_tecnica', 'requiere_condiciones_almacenamiento', 'requiere_certificaciones_sanitarias']:
                if flag in form_data:
                    form_data[flag] = form_data[flag].lower() in ('true', '1', 'yes')
            
            # Validar datos con schema
            validated_data = self.create_schema.load(form_data)
            
            # Procesar archivos
            files = {}
            for file_category in ['technical_sheet', 'storage_conditions', 'health_certifications']:
                if file_category in request.files:
                    file = request.files[file_category]
                    if file and file.filename:
                        files[file_category] = file
            
            # Crear producto
            product = self.service.create_product(validated_data, files, current_user)
            
            # Serializar respuesta
            response_data = self.response_schema.dump(product)
            
            return success_response(
                data=response_data,
                message='Producto creado exitosamente',
                status_code=201
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Datos de entrada inválidos', errors=e.messages, status_code=400)
        except (AppValidationError, ConflictError) as e:
            return error_response(message=str(e), status_code=400)
        except BusinessError as e:
            return error_response(message=str(e), status_code=500)
        except Exception as e:
            logger.exception("Error inesperado al crear producto")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_product(self, product_id: int):
        """
        GET /api/v1/products/<product_id>
        
        Obtiene un producto por ID
        """
        try:
            product = self.service.get_product_by_id(product_id, include_files=True)
            response_data = self.response_schema.dump(product)
            
            return success_response(
                data=response_data,
                message='Producto obtenido exitosamente'
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.exception(f"Error al obtener producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def update_product(self, product_id: int):
        """
        PUT /api/v1/products/<product_id>
        
        Actualiza un producto
        """
        try:
            current_user = getattr(g, 'username', 'system')
            
            # Obtener datos del request (JSON o form)
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
                # Convertir tipos si es necesario
                for field in ['categoria_id', 'unidad_medida_id', 'proveedor_id']:
                    if field in data:
                        data[field] = int(data[field])
                for field in ['precio_compra', 'precio_venta']:
                    if field in data and data[field]:
                        data[field] = float(data[field])
            
            # Validar datos
            validated_data = self.update_schema.load(data)
            
            # Actualizar producto
            product = self.service.update_product(product_id, validated_data, current_user)
            
            # Serializar respuesta
            response_data = self.response_schema.dump(product)
            
            return success_response(
                data=response_data,
                message='Producto actualizado exitosamente'
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Datos de entrada inválidos', errors=e.messages, status_code=400)
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except (AppValidationError, ConflictError) as e:
            return error_response(message=str(e), status_code=400)
        except BusinessError as e:
            return error_response(message=str(e), status_code=500)
        except Exception as e:
            logger.exception(f"Error al actualizar producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def delete_product(self, product_id: int):
        """
        DELETE /api/v1/products/<product_id>
        
        Elimina un producto (soft delete)
        """
        try:
            current_user = getattr(g, 'username', 'system')
            
            success = self.service.delete_product(product_id, current_user)
            
            if success:
                return success_response(message='Producto eliminado exitosamente')
            else:
                return error_response(message='No se pudo eliminar el producto', status_code=500)
                
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except BusinessError as e:
            return error_response(message=str(e), status_code=500)
        except Exception as e:
            logger.exception(f"Error al eliminar producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def search_products(self):
        """
        GET /api/v1/products/search
        
        Busca productos con filtros y paginación
        
        Query params:
        - q: término de búsqueda
        - categoria_id: filtro por categoría
        - proveedor_id: filtro por proveedor
        - status: filtro por estado (active, inactive, discontinued, all)
        - page: página (default: 1)
        - per_page: elementos por página (default: 20, max: 100)
        """
        try:
            # Validar parámetros de búsqueda
            query_params = request.args.to_dict()
            validated_params = self.search_schema.load(query_params)
            
            # Realizar búsqueda
            products, total, metadata = self.service.search_products(**validated_params)
            
            # Serializar resultados
            products_data = [self.list_schema.dump(product) for product in products]
            
            return paginated_response(
                items=products_data,
                page=metadata['page'],
                per_page=metadata['per_page'],
                total=metadata['total'],
                message=f'{len(products)} productos encontrados'
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Parámetros de búsqueda inválidos', errors=e.messages, status_code=400)
        except Exception as e:
            logger.exception("Error en búsqueda de productos")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_products(self):
        """
        GET /api/v1/products
        
        Lista todos los productos (paginado)
        """
        return self.search_products()
    
    def add_product_file(self, product_id: int):
        """
        POST /api/v1/products/<product_id>/files
        
        Agrega un archivo a un producto
        """
        try:
            current_user = getattr(g, 'username', 'system')
            
            # Validar que hay archivo
            if 'file' not in request.files:
                return error_response(message='Debe proporcionar un archivo', status_code=400)
            
            file = request.files['file']
            file_category = request.form.get('file_category')
            description = request.form.get('description')
            
            # Validar datos
            file_data = {
                'file_category': file_category,
                'description': description
            }
            
            # Validación básica
            if not file_category:
                return error_response(message='Debe especificar la categoría del archivo', status_code=400)
            
            if file_category not in ['technical_sheet', 'storage_conditions', 'health_certifications']:
                return error_response(message='Categoría de archivo no válida', status_code=400)
            
            # Agregar archivo
            product_file = self.service.add_product_file(product_id, file, file_category, description, current_user)
            
            return success_response(
                data=product_file.to_dict(),
                message='Archivo agregado exitosamente',
                status_code=201
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except (AppValidationError, BusinessError) as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.exception(f"Error al agregar archivo al producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_product_files(self, product_id: int):
        """
        GET /api/v1/products/<product_id>/files
        
        Obtiene archivos de un producto
        """
        try:
            file_category = request.args.get('file_category')
            files = self.service.get_product_files(product_id, file_category)
            
            files_data = [file.to_dict() for file in files]
            
            return success_response(
                data=files_data,
                message=f'{len(files)} archivos encontrados'
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.exception(f"Error al obtener archivos del producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def delete_product_file(self, file_id: int):
        """
        DELETE /api/v1/products/files/<file_id>
        
        Elimina un archivo de producto
        """
        try:
            success = self.service.delete_product_file(file_id)
            
            if success:
                return success_response(message='Archivo eliminado exitosamente')
            else:
                return error_response(message='No se pudo eliminar el archivo', status_code=500)
                
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except BusinessError as e:
            return error_response(message=str(e), status_code=500)
        except Exception as e:
            logger.exception(f"Error al eliminar archivo {file_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def download_product_file(self, file_id: int):
        """
        GET /api/v1/products/files/<file_id>/download
        
        Descarga un archivo de producto
        """
        try:
            from app.modules.products.repository import ProductFileRepository
            file_repo = ProductFileRepository()
            
            product_file = file_repo.get_file_by_id(file_id)
            file_path = Path(product_file.storage_path)
            
            if not file_path.exists():
                return error_response(message='Archivo no encontrado en el sistema de archivos', status_code=404)
            
            return send_file(
                str(file_path),
                as_attachment=True,
                download_name=product_file.original_filename,
                mimetype=product_file.mime_type
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.exception(f"Error al descargar archivo {file_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_product_catalog_status(self, product_id: int):
        """
        GET /api/v1/products/<product_id>/catalog-status
        
        Obtiene el estado del producto en el catálogo
        """
        try:
            status_info = self.service.get_product_catalog_status(product_id)
            
            return success_response(
                data=status_info,
                message='Estado del catálogo obtenido exitosamente'
            )
            
        except ResourceNotFoundError as e:
            return error_response(message=str(e), status_code=404)
        except Exception as e:
            logger.exception(f"Error al obtener estado del catálogo para producto {product_id}")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_products_missing_documents(self):
        """
        GET /api/v1/products/missing-documents
        
        Obtiene productos que no tienen documentos requeridos
        """
        try:
            products_info = self.service.get_products_missing_documents()
            
            return success_response(
                data=products_info,
                message=f'{len(products_info)} productos con documentos faltantes'
            )
            
        except Exception as e:
            logger.exception("Error al obtener productos con documentos faltantes")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def bulk_upload_products(self):
        """
        POST /api/v1/products/bulk-upload
        
        Carga masiva de productos desde archivo CSV
        
        Admite dos formatos:
        1. Content-Type: multipart/form-data con campo 'csv_file'
        2. Content-Type: text/csv con el contenido CSV en el body
        
        Form fields (para multipart):
        - csv_file (required): Archivo CSV con productos
        
        Raw body (para text/csv):
        - Contenido CSV directo
        
        Estructura esperada del CSV:
        nombre,codigo,descripcion,categoria_id,unidad_medida_id,proveedor_id,referencia,precio_compra,precio_venta,requiere_ficha_tecnica,requiere_condiciones_almacenamiento,requiere_certificaciones_sanitarias
        """
        try:
            current_user = getattr(g, 'username', 'system')
            csv_content = None
            
            # Detectar formato del request
            content_type = request.content_type or ''
            
            if 'multipart/form-data' in content_type:
                # Formato multipart/form-data
                if 'csv_file' not in request.files:
                    return error_response(
                        message='No se proporcionó archivo CSV',
                        status_code=400
                    )
                
                csv_file = request.files['csv_file']
                
                if not csv_file or not csv_file.filename:
                    return error_response(
                        message='No se seleccionó archivo',
                        status_code=400
                    )
                
                # Leer contenido del archivo
                try:
                    csv_content = csv_file.read().decode('utf-8-sig')
                except UnicodeDecodeError:
                    csv_file.seek(0)
                    csv_content = csv_file.read().decode('latin1')
                    
            elif 'text/csv' in content_type:
                # Formato CSV directo en el body
                try:
                    csv_content = request.get_data(as_text=True)
                    if not csv_content:
                        return error_response(
                            message='El contenido CSV está vacío',
                            status_code=400
                        )
                except Exception as e:
                    return error_response(
                        message=f'Error al leer contenido CSV: {str(e)}',
                        status_code=400
                    )
            else:
                return error_response(
                    message=f'Content-Type "{content_type}" no soportado. Use multipart/form-data o text/csv',
                    status_code=400
                )
            
            if not csv_content:
                return error_response(
                    message='No se pudo obtener contenido CSV',
                    status_code=400
                )
            
            # Procesar carga masiva con contenido CSV
            results = self.service.bulk_upload_products_from_content(csv_content, current_user)
            
            # Determinar status code según resultados
            if results['error_count'] == 0:
                status_code = 201  # Todos exitosos
                message = f"Todos los {results['success_count']} productos fueron creados exitosamente"
            elif results['success_count'] == 0:
                status_code = 400  # Todos fallaron
                message = f"No se pudo crear ningún producto. {results['error_count']} errores encontrados"
            else:
                status_code = 207  # Multi-status (algunos exitosos, algunos fallaron)
                message = f"Carga parcialmente exitosa: {results['success_count']} creados, {results['error_count']} errores"
            
            return success_response(
                data=results,
                message=message,
                status_code=status_code
            )
            
        except AppValidationError as e:
            return error_response(message=str(e), status_code=400)
        except ConflictError as e:
            return error_response(message=str(e), status_code=409)
        except BusinessError as e:
            return error_response(message=str(e), status_code=500)
        except Exception as e:
            logger.exception("Error inesperado en carga masiva")
            return error_response(message='Error interno del servidor', status_code=500)


class CategoriaController:
    """Controlador para categorías"""
    
    def __init__(self):
        self.service = CategoriaService()
        self.create_schema = CategoriaCreateSchema()
    
    def create_categoria(self):
        """POST /api/v1/categorias"""
        try:
            current_user = getattr(g, 'username', 'system')
            data = request.get_json()
            validated_data = self.create_schema.load(data)
            
            categoria = self.service.create_categoria(validated_data, current_user)
            
            return success_response(
                data=categoria.to_dict(),
                message='Categoría creada exitosamente',
                status_code=201
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Datos inválidos', errors=e.messages, status_code=400)
        except ConflictError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.exception("Error al crear categoría")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_categorias(self):
        """GET /api/v1/categorias"""
        try:
            categorias = self.service.get_all_categorias()
            categorias_data = [cat.to_dict() for cat in categorias]
            
            return success_response(
                data=categorias_data,
                message=f'{len(categorias)} categorías encontradas'
            )
            
        except Exception as e:
            logger.exception("Error al obtener categorías")
            return error_response(message='Error interno del servidor', status_code=500)


class UnidadMedidaController:
    """Controlador para unidades de medida"""
    
    def __init__(self):
        self.service = UnidadMedidaService()
        self.create_schema = UnidadMedidaCreateSchema()
    
    def create_unidad_medida(self):
        """POST /api/v1/unidades-medida"""
        try:
            current_user = getattr(g, 'username', 'system')
            data = request.get_json()
            validated_data = self.create_schema.load(data)
            
            unidad = self.service.create_unidad_medida(validated_data, current_user)
            
            return success_response(
                data=unidad.to_dict(),
                message='Unidad de medida creada exitosamente',
                status_code=201
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Datos inválidos', errors=e.messages, status_code=400)
        except ConflictError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.exception("Error al crear unidad de medida")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_unidades_medida(self):
        """GET /api/v1/unidades-medida"""
        try:
            unidades = self.service.get_all_unidades_medida()
            unidades_data = [unidad.to_dict() for unidad in unidades]
            
            return success_response(
                data=unidades_data,
                message=f'{len(unidades)} unidades encontradas'
            )
            
        except Exception as e:
            logger.exception("Error al obtener unidades de medida")
            return error_response(message='Error interno del servidor', status_code=500)


class ProveedorController:
    """Controlador para proveedores"""
    
    def __init__(self):
        self.service = ProveedorService()
        self.create_schema = ProveedorCreateSchema()
    
    def create_proveedor(self):
        """POST /api/v1/proveedores"""
        try:
            current_user = getattr(g, 'username', 'system')
            data = request.get_json()
            validated_data = self.create_schema.load(data)
            
            proveedor = self.service.create_proveedor(validated_data, current_user)
            
            return success_response(
                data=proveedor.to_dict(),
                message='Proveedor creado exitosamente',
                status_code=201
            )
            
        except MarshmallowValidationError as e:
            return error_response(message='Datos inválidos', errors=e.messages, status_code=400)
        except ConflictError as e:
            return error_response(message=str(e), status_code=400)
        except Exception as e:
            logger.exception("Error al crear proveedor")
            return error_response(message='Error interno del servidor', status_code=500)
    
    def get_proveedores(self):
        """GET /api/v1/proveedores"""
        try:
            search_term = request.args.get('q')
            
            if search_term:
                proveedores = self.service.search_proveedores(search_term)
                message = f'{len(proveedores)} proveedores encontrados para "{search_term}"'
            else:
                proveedores = self.service.get_all_proveedores()
                message = f'{len(proveedores)} proveedores encontrados'
            
            proveedores_data = [prov.to_dict() for prov in proveedores]
            
            return success_response(
                data=proveedores_data,
                message=message
            )
            
        except Exception as e:
            logger.exception("Error al obtener proveedores")
            return error_response(message='Error interno del servidor', status_code=500)
