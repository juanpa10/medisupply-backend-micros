"""
Excepciones personalizadas
"""


class AppException(Exception):
    """Excepción base de la aplicación"""
    
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class ValidationError(AppException):
    """Error de validación"""
    
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(AppException):
    """Recurso no encontrado"""
    
    def __init__(self, message="Recurso no encontrado", payload=None):
        super().__init__(message, status_code=404, payload=payload)


class UnauthorizedError(AppException):
    """No autorizado"""
    
    def __init__(self, message="No autorizado", payload=None):
        super().__init__(message, status_code=401, payload=payload)


class ForbiddenError(AppException):
    """Acceso prohibido"""
    
    def __init__(self, message="Acceso prohibido", payload=None):
        super().__init__(message, status_code=403, payload=payload)


class ConflictError(AppException):
    """Conflicto (por ejemplo, duplicado)"""
    
    def __init__(self, message="El recurso ya existe", payload=None):
        super().__init__(message, status_code=409, payload=payload)


class FileUploadError(AppException):
    """Error en subida de archivo"""
    
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)
