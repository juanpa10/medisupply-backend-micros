"""
Servicio de lógica de negocio para Suppliers
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.datastructures import FileStorage
from flask import current_app
from app.modules.suppliers.repository import SupplierRepository
from app.modules.suppliers.models import Supplier
from app.core.exceptions import ValidationError, ConflictError, FileUploadError
from app.core.utils.validators import (
    validate_file_extension,
    validate_file_size,
    validate_file_mime_type,
    get_secure_filename
)
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class SupplierService:
    """Servicio para gestión de proveedores"""
    
    def __init__(self):
        self.repository = SupplierRepository()
    
    @staticmethod
    def _normalize_file_path(file_path: str) -> str:
        """
        Normaliza una ruta de archivo para que sea compatible con el sistema operativo.
        Convierte rutas relativas a absolutas y maneja espacios y barras invertidas correctamente.
        
        Args:
            file_path: Ruta del archivo (relativa o absoluta)
            
        Returns:
            Ruta absoluta normalizada como string
        """
        # En Windows, las rutas pueden venir con barras simples o dobles desde la BD
        # Path() maneja ambos casos automáticamente
        path = Path(file_path)
        
        # Si es ruta relativa, convertir a absoluta desde el directorio raíz del proyecto
        if not path.is_absolute():
            # Obtener el directorio raíz del proyecto (3 niveles arriba desde este archivo)
            current_file = Path(__file__).resolve()
            app_root = current_file.parent.parent.parent
            path = app_root / path
        
        # Resolver la ruta (elimina .., ., símbolos, etc.)
        # Path.resolve() maneja automáticamente:
        # - Espacios en las rutas
        # - Barras invertidas en Windows (convierte / a \)
        # - Barras normales en Linux/Mac
        resolved_path = path.resolve()
        
        # Convertir a string con el formato nativo del SO
        # En Windows: C:\Users\... (con barras invertidas)
        # En Linux/Mac: /home/... (con barras normales)
        return str(resolved_path)
    
    def create_supplier(self, data: dict, certificado: FileStorage, user: str = None) -> Supplier:
        """
        Crea un nuevo proveedor
        
        Args:
            data: Datos del proveedor
            certificado: Archivo de certificado
            user: Usuario que crea
            
        Returns:
            Supplier creado
            
        Raises:
            ConflictError: Si el NIT ya existe
            FileUploadError: Si hay problema con el archivo
        """
        # Validar que el NIT no exista
        if self.repository.check_nit_exists(data['nit']):
            raise ConflictError(f'Ya existe un proveedor con el NIT {data["nit"]}')
        
        # Procesar y validar el archivo
        file_info = self._process_certificate_file(certificado)
        
        # Agregar información del archivo a los datos
        data.update({
            'certificado_filename': file_info['filename'],
            'certificado_path': file_info['path'],
            'certificado_mime_type': file_info['mime_type'],
            'certificado_size': file_info['size']
        })
        
        # Crear el proveedor
        supplier = self.repository.create(data, user)
        
        logger.info(
            f'Proveedor creado: {supplier.razon_social} (NIT: {supplier.nit}) '
            f'por usuario {user}'
        )
        
        return supplier
    
    def get_supplier(self, supplier_id: int) -> Supplier:
        """
        Obtiene un proveedor por ID
        
        Args:
            supplier_id: ID del proveedor
            
        Returns:
            Supplier
        """
        return self.repository.get_by_id_or_fail(supplier_id)
    
    def get_all_suppliers(self, search: str = None, pais: str = None, 
                          status: str = None):
        """
        Obtiene todos los proveedores con filtros opcionales
        
        Args:
            search: Término de búsqueda
            pais: Filtro por país
            status: Filtro por estado
            
        Returns:
            Query de proveedores
        """
        return self.repository.search_suppliers(search, pais, status)
    
    def update_supplier(self, supplier_id: int, data: dict, 
                       certificado: FileStorage = None, user: str = None) -> Supplier:
        """
        Actualiza un proveedor
        
        Args:
            supplier_id: ID del proveedor
            data: Datos a actualizar
            certificado: Nuevo certificado (opcional)
            user: Usuario que actualiza
            
        Returns:
            Supplier actualizado
        """
        # Verificar que el proveedor existe
        supplier = self.repository.get_by_id_or_fail(supplier_id)
        
        # Si se envía un nuevo certificado, procesarlo
        if certificado:
            # Eliminar el archivo anterior
            self._delete_certificate_file(supplier.certificado_path)
            
            # Procesar nuevo archivo
            file_info = self._process_certificate_file(certificado)
            data.update({
                'certificado_filename': file_info['filename'],
                'certificado_path': file_info['path'],
                'certificado_mime_type': file_info['mime_type'],
                'certificado_size': file_info['size']
            })
        
        # Actualizar
        supplier = self.repository.update(supplier_id, data, user)
        
        logger.info(
            f'Proveedor actualizado: {supplier.razon_social} (ID: {supplier_id}) '
            f'por usuario {user}'
        )
        
        return supplier
    
    def delete_supplier(self, supplier_id: int, user: str = None) -> bool:
        """
        Elimina un proveedor (soft delete)
        
        Args:
            supplier_id: ID del proveedor
            user: Usuario que elimina
            
        Returns:
            True si se eliminó
        """
        supplier = self.repository.get_by_id_or_fail(supplier_id)
        
        result = self.repository.delete(supplier_id, user, soft=True)
        
        logger.info(
            f'Proveedor eliminado: {supplier.razon_social} (ID: {supplier_id}) '
            f'por usuario {user}'
        )
        
        return result
    
    def get_suppliers_count(self) -> int:
        """
        Obtiene el conteo total de proveedores activos
        
        Returns:
            Número de proveedores
        """
        return self.repository.count()
    
    def get_by_nit(self, nit: str):
        """
        Obtiene un proveedor por NIT
        
        Args:
            nit: NIT del proveedor
            
        Returns:
            Supplier o None
        """
        return self.repository.get_by_nit(nit)
    
    def get_supplier_certificate(self, supplier_id: int) -> dict:
        """
        Obtiene la información del certificado de un proveedor
        
        Args:
            supplier_id: ID del proveedor
            
        Returns:
            dict con información del archivo (path, filename, mime_type, size)
            
        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        # Obtener el proveedor
        supplier = self.repository.get_by_id_or_fail(supplier_id)
        
        # Normalizar la ruta del archivo (maneja espacios, rutas relativas, etc.)
        file_path = self._normalize_file_path(supplier.certificado_path)
        
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            logger.error(
                f'Archivo de certificado no encontrado: {file_path} '
                f'(ruta almacenada: {supplier.certificado_path}) '
                f'para proveedor {supplier.razon_social} (ID: {supplier_id})'
            )
            raise FileNotFoundError(
                'El archivo de certificado no existe en el servidor'
            )
        
        logger.info(
            f'Certificado solicitado para proveedor: {supplier.razon_social} '
            f'(ID: {supplier_id}), ruta: {file_path}'
        )
        
        return {
            'path': file_path,
            'filename': supplier.certificado_filename,
            'mime_type': supplier.certificado_mime_type,
            'size': supplier.certificado_size
        }
    
    def _process_certificate_file(self, file: FileStorage) -> dict:
        """
        Procesa y guarda el archivo de certificado
        
        Args:
            file: Archivo a procesar
            
        Returns:
            dict con información del archivo guardado
            
        Raises:
            FileUploadError: Si hay error en el archivo
        """
        if not file or file.filename == '':
            raise FileUploadError('No se proporcionó ningún archivo')
        
        # Validar extensión
        validate_file_extension(
            file.filename,
            current_app.config['ALLOWED_EXTENSIONS']
        )
        
        # Validar tamaño
        validate_file_size(file, current_app.config['MAX_FILE_SIZE'])
        
        # Validar tipo MIME
        validate_file_mime_type(file)
        
        # Generar nombre único para el archivo
        original_filename = get_secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f'{uuid.uuid4().hex}.{extension}'
        
        # Obtener el directorio raíz del proyecto (3 niveles arriba desde este archivo)
        # Esto asegura que siempre trabajemos desde crm-service/ y no desde app/
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parent.parent.parent  # Desde service.py -> suppliers -> modules -> app -> crm-service
        
        # Construir la ruta usando el upload_folder de configuración
        upload_folder_config = current_app.config['UPLOAD_FOLDER']
        
        # Si upload_folder es relativo, convertirlo a absoluto desde project_root
        upload_folder = Path(upload_folder_config)
        if not upload_folder.is_absolute():
            upload_folder = project_root / upload_folder
        
        certificates_folder = upload_folder / 'certificates'
        certificates_folder.mkdir(parents=True, exist_ok=True)
        
        # Ruta completa del archivo usando pathlib
        file_path = certificates_folder / unique_filename
        
        # Resolver la ruta para obtener la ruta absoluta normalizada
        file_path_resolved = file_path.resolve()
        
        # Guardar archivo (convertir Path a string para FileStorage.save())
        file.save(str(file_path_resolved))
        
        # Obtener tamaño del archivo
        file_size = file_path_resolved.stat().st_size
        
        # Obtener tipo MIME
        file.seek(0)
        import magic
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        
        logger.info(f'Archivo de certificado guardado: {unique_filename} en {file_path_resolved}')
        
        # Guardar la ruta absoluta completa en la BD
        # pathlib maneja automáticamente las barras invertidas
        return {
            'filename': original_filename,
            'path': str(file_path_resolved),  # Ruta absoluta normalizada para guardar en DB
            'mime_type': mime_type,
            'size': file_size
        }
    
    def _delete_certificate_file(self, file_path: str):
        """
        Elimina un archivo de certificado del sistema
        
        Args:
            file_path: Ruta del archivo a eliminar
        """
        try:
            # Normalizar la ruta del archivo
            normalized_path = self._normalize_file_path(file_path)
            
            # Usar pathlib para manejo seguro
            path = Path(normalized_path)
            
            if path.exists() and path.is_file():
                path.unlink()  # Método de pathlib para eliminar archivos
                logger.info(f'Archivo eliminado: {normalized_path}')
            else:
                logger.warning(f'Archivo no encontrado para eliminar: {normalized_path}')
        except Exception as e:
            logger.warning(f'No se pudo eliminar el archivo {file_path}: {str(e)}')
