"""
Servicio de lógica de negocio para productos

Maneja:
- Creación y gestión de productos
- Gestión de archivos adjuntos
- Validaciones de negocio
- Disponibilidad en catálogo
"""
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from pathlib import Path
from werkzeug.datastructures import FileStorage
from flask import current_app, g
from app.modules.products.repository import (
    ProductRepository, ProductFileRepository, CategoriaRepository,
    UnidadMedidaRepository, ProveedorRepository
)
from app.modules.products.models import Product, ProductFile, Categoria, UnidadMedida, Proveedor
from app.core.exceptions import ValidationError, ConflictError, BusinessError, ResourceNotFoundError
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class ProductService:
    """Servicio para gestión de productos"""
    
    def __init__(self):
        self.product_repo = ProductRepository()
        self.file_repo = ProductFileRepository()
        self.categoria_repo = CategoriaRepository()
        self.unidad_repo = UnidadMedidaRepository()
        self.proveedor_repo = ProveedorRepository()
    
    def create_product(
        self,
        product_data: Dict[str, Any],
        files: Optional[Dict[str, FileStorage]] = None,
        current_user: Optional[str] = None
    ) -> Product:
        """
        Crea un nuevo producto con archivos opcionales
        
        Args:
            product_data: Datos del producto
            files: Archivos organizados por categoría {'technical_sheet': file, ...}
            current_user: Usuario actual
            
        Returns:
            Product: Producto creado
        """
        logger.info(f"Creando producto: {product_data.get('codigo', 'N/A')}")
        
        # Validar que el código no exista
        existing_product = self.product_repo.get_product_by_codigo(product_data['codigo'])
        if existing_product:
            raise ConflictError(f"Ya existe un producto con el código '{product_data['codigo']}'")
        
        # Validar referencias FK
        self._validate_foreign_keys(product_data)
        
        # Agregar usuario creador
        if current_user:
            product_data['created_by'] = current_user
        
        try:
            # Crear producto
            product = self.product_repo.create_product(product_data)
            
            # Procesar archivos si se proporcionaron
            if files:
                self._process_product_files(product.id, files, current_user)
            
            # Recargar producto con archivos
            product_with_files = self.product_repo.get_product_by_id(product.id, include_relations=True)
            
            logger.info(f"Producto creado exitosamente: {product.id} - {product.codigo}")
            return product_with_files
            
        except Exception as e:
            logger.error(f"Error al crear producto: {str(e)}")
            raise BusinessError(f"Error al crear producto: {str(e)}")
    
    def get_product_by_id(self, product_id: int, include_files: bool = True) -> Product:
        """
        Obtiene un producto por ID
        """
        return self.product_repo.get_product_by_id(product_id, include_relations=include_files)
    
    def update_product(
        self,
        product_id: int,
        update_data: Dict[str, Any],
        current_user: Optional[str] = None
    ) -> Product:
        """
        Actualiza un producto
        """
        logger.info(f"Actualizando producto: {product_id}")
        
        # Verificar que el producto existe
        existing_product = self.product_repo.get_product_by_id(product_id, include_relations=False)
        
        # Si se está actualizando el código, verificar que no exista
        if 'codigo' in update_data and update_data['codigo'] != existing_product.codigo:
            duplicate = self.product_repo.get_product_by_codigo(update_data['codigo'])
            if duplicate:
                raise ConflictError(f"Ya existe un producto con el código '{update_data['codigo']}'")
        
        # Validar referencias FK si se están actualizando
        if any(key in update_data for key in ['categoria_id', 'unidad_medida_id', 'proveedor_id']):
            self._validate_foreign_keys(update_data, partial=True)
        
        # Agregar usuario actualizador
        if current_user:
            update_data['updated_by'] = current_user
        
        try:
            product = self.product_repo.update_product(product_id, update_data)
            logger.info(f"Producto actualizado: {product_id}")
            return product
            
        except Exception as e:
            logger.error(f"Error al actualizar producto {product_id}: {str(e)}")
            raise BusinessError(f"Error al actualizar producto: {str(e)}")
    
    def search_products(
        self,
        search_term: Optional[str] = None,
        categoria_id: Optional[int] = None,
        proveedor_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Product], int, Dict[str, Any]]:
        """
        Busca productos con filtros y metadatos
        
        Returns:
            Tuple[List[Product], int, Dict]: Productos, total, metadata
        """
        products, total = self.product_repo.search_products(
            search_term=search_term,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id,
            status=status,
            page=page,
            per_page=per_page
        )
        
        # Metadata de paginación
        total_pages = (total + per_page - 1) // per_page
        metadata = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
        
        return products, total, metadata
    
    def delete_product(self, product_id: int, current_user: Optional[str] = None) -> bool:
        """
        Elimina un producto (soft delete)
        """
        logger.info(f"Eliminando producto: {product_id}")
        
        try:
            product = self.product_repo.get_product_by_id(product_id, include_relations=False)
            
            # Marcar archivos como eliminados
            files = self.file_repo.get_files_by_product(product_id)
            for file in files:
                file.status = 'deleted'
            
            # Soft delete del producto
            product.soft_delete(current_user)
            
            from app.config.database import db
            db.session.commit()
            
            logger.info(f"Producto eliminado: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar producto {product_id}: {str(e)}")
            raise BusinessError(f"Error al eliminar producto: {str(e)}")
    
    def add_product_file(
        self,
        product_id: int,
        file: FileStorage,
        file_category: str,
        description: Optional[str] = None,
        current_user: Optional[str] = None
    ) -> ProductFile:
        """
        Agrega un archivo a un producto
        """
        logger.info(f"Agregando archivo {file_category} al producto {product_id}")
        
        # Verificar que el producto existe
        self.product_repo.get_product_by_id(product_id, include_relations=False)
        
        try:
            file_data = self._save_uploaded_file(file, file_category, current_user)
            file_data['product_id'] = product_id
            file_data['description'] = description
            
            product_file = self.file_repo.create_file(file_data)
            logger.info(f"Archivo agregado: {product_file.id} - {product_file.original_filename}")
            return product_file
            
        except Exception as e:
            logger.error(f"Error al agregar archivo al producto {product_id}: {str(e)}")
            raise BusinessError(f"Error al agregar archivo: {str(e)}")
    
    def get_product_files(self, product_id: int, file_category: Optional[str] = None) -> List[ProductFile]:
        """
        Obtiene archivos de un producto
        """
        return self.file_repo.get_files_by_product(product_id, file_category)
    
    def delete_product_file(self, file_id: int) -> bool:
        """
        Elimina un archivo de producto
        """
        logger.info(f"Eliminando archivo: {file_id}")
        
        try:
            result = self.file_repo.delete_file(file_id)
            logger.info(f"Archivo eliminado: {file_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error al eliminar archivo {file_id}: {str(e)}")
            raise BusinessError(f"Error al eliminar archivo: {str(e)}")
    
    def get_product_catalog_status(self, product_id: int) -> Dict[str, Any]:
        """
        Obtiene el estado del producto en el catálogo
        """
        product = self.product_repo.get_product_by_id(product_id, include_relations=True)
        status, message = product.get_catalog_status()
        
        return {
            'product_id': product_id,
            'catalog_status': status,
            'message': message,
            'has_required_documents': product.has_required_documents(),
            'required_documents': {
                'technical_sheet': product.requiere_ficha_tecnica,
                'storage_conditions': product.requiere_condiciones_almacenamiento,
                'health_certifications': product.requiere_certificaciones_sanitarias
            },
            'uploaded_documents': {
                file.file_category: True for file in product.files if file.status == 'active'
            }
        }
    
    def get_products_missing_documents(self) -> List[Dict[str, Any]]:
        """
        Obtiene productos que no tienen documentos requeridos
        """
        products = self.product_repo.get_products_without_required_documents()
        
        result = []
        for product in products:
            status_info = self.get_product_catalog_status(product.id)
            result.append({
                'product': product.to_dict(),
                'catalog_info': status_info
            })
        
        return result
    
    # ========== Métodos privados ==========
    
    def _validate_foreign_keys(self, data: Dict[str, Any], partial: bool = False):
        """
        Valida que las referencias FK existan
        """
        if 'categoria_id' in data:
            try:
                self.categoria_repo.get_by_id(data['categoria_id'])
            except ResourceNotFoundError:
                raise ValidationError(f"Categoría con ID {data['categoria_id']} no encontrada")
        
        if 'unidad_medida_id' in data:
            try:
                self.unidad_repo.get_by_id(data['unidad_medida_id'])
            except ResourceNotFoundError:
                raise ValidationError(f"Unidad de medida con ID {data['unidad_medida_id']} no encontrada")
        
        if 'proveedor_id' in data:
            try:
                self.proveedor_repo.get_by_id(data['proveedor_id'])
            except ResourceNotFoundError:
                raise ValidationError(f"Proveedor con ID {data['proveedor_id']} no encontrado")
    
    def _process_product_files(
        self,
        product_id: int,
        files: Dict[str, FileStorage],
        current_user: Optional[str] = None
    ):
        """
        Procesa múltiples archivos de producto
        """
        for file_category, file in files.items():
            if file and file.filename:
                try:
                    self.add_product_file(product_id, file, file_category, current_user=current_user)
                except Exception as e:
                    logger.warning(f"Error al procesar archivo {file_category}: {str(e)}")
                    # Continuar con otros archivos
    
    def _save_uploaded_file(
        self,
        file: FileStorage,
        file_category: str,
        current_user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Guarda un archivo subido y retorna metadatos
        """
        if not file or not file.filename:
            raise ValidationError("Archivo no válido")
        
        # Validaciones básicas
        self._validate_file(file)
        
        # Generar nombre único
        file_extension = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        stored_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Definir directorio de almacenamiento
        upload_dir = self._get_upload_directory()
        file_path = upload_dir / stored_filename
        
        try:
            # Asegurar que el directorio existe
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo
            file.save(str(file_path))
            
            # Obtener tamaño real del archivo
            file_size = file_path.stat().st_size
            
            return {
                'file_category': file_category,
                'original_filename': file.filename,
                'stored_filename': stored_filename,
                'mime_type': file.content_type or 'application/octet-stream',
                'file_extension': file_extension,
                'file_size_bytes': file_size,
                'storage_path': str(file_path),
                'uploaded_by_user_id': getattr(g, 'user_id', None),
                'uploaded_by_username': current_user
            }
            
        except Exception as e:
            # Limpiar archivo si hubo error
            if file_path.exists():
                file_path.unlink()
            raise BusinessError(f"Error al guardar archivo: {str(e)}")
    
    def _validate_file(self, file: FileStorage):
        """
        Valida un archivo subido
        """
        # Extensiones permitidas
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise ValidationError(f'Extensión no permitida. Permitidas: {", ".join(allowed_extensions)}')
        
        # Tamaño máximo (5MB)
        max_size = 5 * 1024 * 1024
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > max_size:
                raise ValidationError('El archivo no puede exceder 5MB')
    
    def _get_upload_directory(self) -> Path:
        """
        Obtiene el directorio de subida de archivos
        """
        upload_path = current_app.config.get('UPLOAD_FOLDER', 'uploads/products')
        return Path(upload_path)
    
    def bulk_upload_products(
        self,
        csv_file: FileStorage,
        current_user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Carga masiva de productos desde archivo CSV
        
        Args:
            csv_file: Archivo CSV con los datos de productos
            current_user: Usuario actual
            
        Returns:
            Dict con resumen de la operación
        """
        import csv
        import io
        from app.modules.products.schemas import ProductBulkUploadSchema
        
        logger.info(f"Iniciando carga masiva de productos por usuario: {current_user}")
        
        # Validar archivo
        if not csv_file or not csv_file.filename:
            raise ValidationError("No se proporcionó archivo CSV")
        
        if not csv_file.filename.lower().endswith('.csv'):
            raise ValidationError("El archivo debe ser un CSV")
        
        # Leer contenido del archivo
        try:
            # Decodificar contenido del CSV
            content = csv_file.read().decode('utf-8-sig')  # utf-8-sig maneja BOM de Excel
            csv_data = io.StringIO(content)
            csv_reader = csv.DictReader(csv_data)
            
        except UnicodeDecodeError:
            # Intentar con latin1 si UTF-8 falla
            csv_file.seek(0)
            content = csv_file.read().decode('latin1')
            csv_data = io.StringIO(content)
            csv_reader = csv.DictReader(csv_data)
        except Exception as e:
            raise ValidationError(f"Error al leer archivo CSV: {str(e)}")
        
        # Validar estructura del CSV
        expected_columns = {
            'nombre', 'codigo', 'descripcion', 'categoria_id', 
            'unidad_medida_id', 'proveedor_id'
        }
        optional_columns = {
            'referencia', 'precio_compra', 'precio_venta',
            'requiere_ficha_tecnica', 'requiere_condiciones_almacenamiento',
            'requiere_certificaciones_sanitarias'
        }
        
        if not csv_reader.fieldnames:
            raise ValidationError("El archivo CSV está vacío o no tiene encabezados")
        
        csv_columns = set(col.strip().lower() for col in csv_reader.fieldnames if col)
        missing_required = expected_columns - csv_columns
        
        if missing_required:
            raise ValidationError(
                f"El CSV debe contener las columnas obligatorias: {', '.join(sorted(missing_required))}"
            )
        
        # Procesar filas del CSV
        schema = ProductBulkUploadSchema()
        results = {
            'success_count': 0,
            'error_count': 0,
            'errors': [],
            'created_products': []
        }
        
        row_number = 1  # Para reportar errores
        
        for row in csv_reader:
            row_number += 1
            
            try:
                # Limpiar datos de la fila
                clean_row = {}
                for key, value in row.items():
                    if key and value is not None:
                        clean_key = key.strip().lower()
                        clean_value = str(value).strip() if value else None
                        
                        # Convertir valores booleanos
                        if clean_key.startswith('requiere_'):
                            if clean_value and clean_value.lower() in ('true', '1', 'sí', 'si', 'yes'):
                                clean_value = True
                            elif clean_value and clean_value.lower() in ('false', '0', 'no'):
                                clean_value = False
                            else:
                                clean_value = False
                        
                        # Convertir valores numéricos
                        if clean_key.endswith('_id') and clean_value:
                            try:
                                clean_value = int(clean_value)
                            except ValueError:
                                raise ValidationError(f"El campo {clean_key} debe ser un número entero")
                        
                        if clean_key.startswith('precio_') and clean_value:
                            try:
                                clean_value = float(clean_value)
                            except ValueError:
                                raise ValidationError(f"El campo {clean_key} debe ser un número decimal")
                        
                        clean_row[clean_key] = clean_value
                
                # Validar datos con schema
                validated_data = schema.load(clean_row)
                
                # Verificar que no existe producto con el mismo código
                existing = self.product_repo.get_product_by_codigo(validated_data['codigo'])
                if existing:
                    raise ConflictError(f"Ya existe un producto con código '{validated_data['codigo']}'")
                
                # Validar foreign keys
                self._validate_foreign_keys(validated_data)
                
                # Agregar usuario creador
                if current_user:
                    validated_data['created_by'] = current_user
                
                # Crear producto
                product = self.product_repo.create_product(validated_data)
                
                results['created_products'].append({
                    'id': product.id,
                    'codigo': product.codigo,
                    'nombre': product.nombre
                })
                results['success_count'] += 1
                
                logger.info(f"Producto creado desde CSV: {product.codigo} - {product.nombre}")
                
            except Exception as e:
                error_msg = f"Fila {row_number}: {str(e)}"
                results['errors'].append(error_msg)
                results['error_count'] += 1
                logger.warning(f"Error procesando fila {row_number}: {str(e)}")
        
        # Log final
        logger.info(f"Carga masiva completada - Exitosos: {results['success_count']}, Errores: {results['error_count']}")
        
        return results
    
    def bulk_upload_products_from_content(
        self,
        csv_content: str,
        current_user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Carga masiva de productos desde contenido CSV directo
        
        Args:
            csv_content: Contenido del CSV como string
            current_user: Usuario actual
            
        Returns:
            Dict con resumen de la operación
        """
        import csv
        import io
        from app.modules.products.schemas import ProductBulkUploadSchema
        
        logger.info(f"Iniciando carga masiva de productos desde contenido CSV por usuario: {current_user}")
        
        # Validar contenido
        if not csv_content or not csv_content.strip():
            raise ValidationError("El contenido CSV está vacío")
        
        # Leer contenido del CSV
        try:
            csv_data = io.StringIO(csv_content)
            csv_reader = csv.DictReader(csv_data)
            
        except Exception as e:
            raise ValidationError(f"Error al procesar contenido CSV: {str(e)}")
        
        # Validar estructura del CSV
        expected_columns = {
            'nombre', 'codigo', 'descripcion', 'categoria_id', 
            'unidad_medida_id', 'proveedor_id'
        }
        optional_columns = {
            'referencia', 'precio_compra', 'precio_venta',
            'requiere_ficha_tecnica', 'requiere_condiciones_almacenamiento',
            'requiere_certificaciones_sanitarias'
        }
        
        if not csv_reader.fieldnames:
            raise ValidationError("El CSV está vacío o no tiene encabezados")
        
        csv_columns = set(col.strip().lower() for col in csv_reader.fieldnames if col)
        missing_required = expected_columns - csv_columns
        
        if missing_required:
            raise ValidationError(
                f"El CSV debe contener las columnas obligatorias: {', '.join(sorted(missing_required))}"
            )
        
        # Procesar filas del CSV
        schema = ProductBulkUploadSchema()
        results = {
            'success_count': 0,
            'error_count': 0,
            'errors': [],
            'created_products': []
        }
        
        row_number = 1  # Para reportar errores
        
        for row in csv_reader:
            row_number += 1
            
            try:
                # Limpiar datos de la fila
                clean_row = {}
                for key, value in row.items():
                    if key and value is not None:
                        clean_key = key.strip().lower()
                        clean_value = str(value).strip() if value else None
                        
                        # Convertir valores booleanos
                        if clean_key.startswith('requiere_'):
                            if clean_value and clean_value.lower() in ('true', '1', 'sí', 'si', 'yes'):
                                clean_value = True
                            elif clean_value and clean_value.lower() in ('false', '0', 'no'):
                                clean_value = False
                            else:
                                clean_value = False
                        
                        # Convertir valores numéricos
                        if clean_key.endswith('_id') and clean_value:
                            try:
                                clean_value = int(clean_value)
                            except ValueError:
                                raise ValidationError(f"El campo {clean_key} debe ser un número entero")
                        
                        if clean_key.startswith('precio_') and clean_value:
                            try:
                                clean_value = float(clean_value)
                            except ValueError:
                                raise ValidationError(f"El campo {clean_key} debe ser un número decimal")
                        
                        clean_row[clean_key] = clean_value
                
                # Validar datos con schema
                validated_data = schema.load(clean_row)
                
                # Verificar que no existe producto con el mismo código
                existing = self.product_repo.get_product_by_codigo(validated_data['codigo'])
                if existing:
                    raise ConflictError(f"Ya existe un producto con código '{validated_data['codigo']}'")
                
                # Validar foreign keys
                self._validate_foreign_keys(validated_data)
                
                # Agregar usuario creador
                if current_user:
                    validated_data['created_by'] = current_user
                
                # Crear producto
                product = self.product_repo.create_product(validated_data)
                
                results['created_products'].append({
                    'id': product.id,
                    'codigo': product.codigo,
                    'nombre': product.nombre
                })
                results['success_count'] += 1
                
                logger.info(f"Producto creado desde CSV: {product.codigo} - {product.nombre}")
                
            except Exception as e:
                error_msg = f"Fila {row_number}: {str(e)}"
                results['errors'].append(error_msg)
                results['error_count'] += 1
                logger.warning(f"Error procesando fila {row_number}: {str(e)}")
        
        # Log final
        logger.info(f"Carga masiva completada - Exitosos: {results['success_count']}, Errores: {results['error_count']}")
        
        return results


class CategoriaService:
    """Servicio para gestión de categorías"""
    
    def __init__(self):
        self.repo = CategoriaRepository()
    
    def create_categoria(self, categoria_data: Dict[str, Any], current_user: Optional[str] = None) -> Categoria:
        """Crea una nueva categoría"""
        # Verificar que no exista
        existing = self.repo.get_categoria_by_nombre(categoria_data['nombre'])
        if existing:
            raise ConflictError(f"Ya existe una categoría con el nombre '{categoria_data['nombre']}'")
        
        if current_user:
            categoria_data['created_by'] = current_user
        
        return self.repo.create_categoria(categoria_data)
    
    def get_all_categorias(self) -> List[Categoria]:
        """Obtiene todas las categorías activas"""
        return self.repo.get_all_categorias()


class UnidadMedidaService:
    """Servicio para gestión de unidades de medida"""
    
    def __init__(self):
        self.repo = UnidadMedidaRepository()
    
    def create_unidad_medida(self, unidad_data: Dict[str, Any], current_user: Optional[str] = None) -> UnidadMedida:
        """Crea una nueva unidad de medida"""
        # Verificar que no exista por nombre o abreviatura
        existing_nombre = self.repo.get_unidad_by_nombre(unidad_data['nombre'])
        if existing_nombre:
            raise ConflictError(f"Ya existe una unidad con el nombre '{unidad_data['nombre']}'")
        
        existing_abrev = self.repo.get_unidad_by_abreviatura(unidad_data['abreviatura'])
        if existing_abrev:
            raise ConflictError(f"Ya existe una unidad con la abreviatura '{unidad_data['abreviatura']}'")
        
        if current_user:
            unidad_data['created_by'] = current_user
        
        return self.repo.create_unidad_medida(unidad_data)
    
    def get_all_unidades_medida(self) -> List[UnidadMedida]:
        """Obtiene todas las unidades de medida activas"""
        return self.repo.get_all_unidades_medida()


class ProveedorService:
    """Servicio para gestión de proveedores"""
    
    def __init__(self):
        self.repo = ProveedorRepository()
    
    def create_proveedor(self, proveedor_data: Dict[str, Any], current_user: Optional[str] = None) -> Proveedor:
        """Crea un nuevo proveedor"""
        # Verificar NIT único si se proporciona
        if proveedor_data.get('nit'):
            existing = self.repo.get_proveedor_by_nit(proveedor_data['nit'])
            if existing:
                raise ConflictError(f"Ya existe un proveedor con el NIT '{proveedor_data['nit']}'")
        
        if current_user:
            proveedor_data['created_by'] = current_user
        
        return self.repo.create_proveedor(proveedor_data)
    
    def get_all_proveedores(self) -> List[Proveedor]:
        """Obtiene todos los proveedores activos"""
        return self.repo.get_all_proveedores()
    
    def search_proveedores(self, search_term: str) -> List[Proveedor]:
        """Busca proveedores por término"""
        return self.repo.search_proveedores(search_term)