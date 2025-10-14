"""
Servicio de lógica de negocio para Suppliers
"""
import os
import uuid
from datetime import datetime
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
        
        # Crear directorio si no existe
        upload_folder = current_app.config['UPLOAD_FOLDER']
        certificates_folder = os.path.join(upload_folder, 'certificates')
        os.makedirs(certificates_folder, exist_ok=True)
        
        # Ruta completa del archivo
        file_path = os.path.join(certificates_folder, unique_filename)
        
        # Guardar archivo
        file.save(file_path)
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(file_path)
        
        # Obtener tipo MIME
        file.seek(0)
        import magic
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        
        logger.info(f'Archivo de certificado guardado: {unique_filename}')
        
        return {
            'filename': original_filename,
            'path': file_path,
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
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f'Archivo eliminado: {file_path}')
        except Exception as e:
            logger.warning(f'No se pudo eliminar el archivo {file_path}: {str(e)}')
