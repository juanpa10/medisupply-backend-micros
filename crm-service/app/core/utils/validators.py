"""
Validadores comunes
"""
import re
import os
import magic
from werkzeug.utils import secure_filename
from app.core.exceptions import ValidationError, FileUploadError
from app.core.constants import ALLOWED_FILE_FORMATS


def validate_email(email):
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el formato es inválido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Formato de email inválido')
    return True


def validate_phone(phone):
    """
    Valida formato de teléfono
    
    Args:
        phone: Número de teléfono
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el formato es inválido
    """
    # Permitir solo números y opcionalmente + al inicio
    pattern = r'^\+?[0-9]{7,15}$'
    if not re.match(pattern, phone):
        raise ValidationError('Formato de teléfono inválido')
    return True


def validate_nit(nit):
    """
    Valida formato de NIT
    
    Args:
        nit: NIT a validar
        
    Returns:
        bool: True si es válido
        
    Raises:
        ValidationError: Si el formato es inválido
    """
    # NIT puede contener números y guiones
    pattern = r'^[0-9\-]{5,20}$'
    if not re.match(pattern, nit):
        raise ValidationError('Formato de NIT inválido')
    return True


def validate_required_fields(data, required_fields):
    """
    Valida que los campos requeridos estén presentes y no vacíos
    
    Args:
        data: Diccionario con los datos
        required_fields: Lista de campos requeridos
        
    Raises:
        ValidationError: Si falta algún campo o está vacío
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f'Campos faltantes: {", ".join(missing_fields)}'
        )
    
    if empty_fields:
        raise ValidationError(
            f'Campos vacíos: {", ".join(empty_fields)}'
        )


def validate_file_extension(filename, allowed_extensions=None):
    """
    Valida la extensión del archivo
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Lista de extensiones permitidas
        
    Returns:
        bool: True si es válida
        
    Raises:
        FileUploadError: Si la extensión no es permitida
    """
    if allowed_extensions is None:
        allowed_extensions = list(ALLOWED_FILE_FORMATS.keys())
    
    if '.' not in filename:
        raise FileUploadError('El archivo debe tener una extensión')
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        raise FileUploadError(
            f'Formato de archivo no permitido. Formatos permitidos: {", ".join(allowed_extensions)}'
        )
    
    return True


def validate_file_size(file, max_size):
    """
    Valida el tamaño del archivo
    
    Args:
        file: Objeto de archivo
        max_size: Tamaño máximo en bytes
        
    Returns:
        bool: True si es válido
        
    Raises:
        FileUploadError: Si excede el tamaño máximo
    """
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise FileUploadError(
            f'El archivo excede el tamaño máximo permitido de {max_mb:.1f}MB'
        )
    
    return True


def validate_file_mime_type(file):
    """
    Valida el tipo MIME del archivo
    
    Args:
        file: Objeto de archivo
        
    Returns:
        bool: True si es válido
        
    Raises:
        FileUploadError: Si el tipo MIME no es permitido
    """
    try:
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        
        allowed_mimes = list(ALLOWED_FILE_FORMATS.values())
        if mime not in allowed_mimes:
            raise FileUploadError(f'Tipo de archivo no permitido: {mime}')
        
        return True
    except Exception as e:
        raise FileUploadError(f'Error al validar el archivo: {str(e)}')


def get_secure_filename(filename):
    """
    Obtiene un nombre de archivo seguro
    
    Args:
        filename: Nombre original del archivo
        
    Returns:
        str: Nombre seguro
    """
    return secure_filename(filename)
