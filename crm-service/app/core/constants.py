"""
Constantes globales
"""

# Formatos de archivo permitidos
ALLOWED_FILE_FORMATS = {
    'pdf': 'application/pdf',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'txt': 'text/plain'
}

# Estados
STATUS_ACTIVE = 'active'
STATUS_INACTIVE = 'inactive'
STATUS_DELETED = 'deleted'

# Roles
ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'
ROLE_OPERATOR = 'operator'

# Mensajes
MSG_SUCCESS_CREATE = 'Registro creado exitosamente'
MSG_SUCCESS_UPDATE = 'Registro actualizado exitosamente'
MSG_SUCCESS_DELETE = 'Registro eliminado exitosamente'
MSG_ERROR_NOT_FOUND = 'Registro no encontrado'
MSG_ERROR_DUPLICATE = 'El registro ya existe'
MSG_ERROR_VALIDATION = 'Error de validación'
MSG_ERROR_UNAUTHORIZED = 'No autorizado'
MSG_ERROR_FILE_FORMAT = 'Formato de archivo no permitido'
MSG_ERROR_FILE_SIZE = 'El archivo excede el tamaño máximo permitido'
