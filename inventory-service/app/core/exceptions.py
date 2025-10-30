"""
Excepciones personalizadas
"""


class AppException(Exception):
    """Excepción base de la aplicación"""
    
    def __init__(self, message, status_code=400, payload=None):
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
    
    def __init__(self, message, errors=None):
        super().__init__(message, 400, errors)


class NotFoundError(AppException):
    """Recurso no encontrado"""
    
    def __init__(self, message='Recurso no encontrado'):
        super().__init__(message, 404)


class ResourceNotFoundError(AppException):
    """Recurso no encontrado (alias de NotFoundError)"""
    
    def __init__(self, message='Recurso no encontrado'):
        super().__init__(message, 404)


class BusinessError(AppException):
    """Error de lógica de negocio"""
    
    def __init__(self, message, status_code=400):
        super().__init__(message, status_code)


class ConflictError(AppException):
    """Conflicto con el estado actual"""
    
    def __init__(self, message='Conflicto con el recurso existente'):
        super().__init__(message, 409)


class UnauthorizedError(AppException):
    """No autorizado"""
    
    def __init__(self, message='No autorizado'):
        super().__init__(message, 401)


class ForbiddenError(AppException):
    """Acceso prohibido"""
    
    def __init__(self, message='Acceso prohibido'):
        super().__init__(message, 403)


class SearchTimeoutError(AppException):
    """Timeout en búsqueda"""
    
    def __init__(self, message='La búsqueda excedió el tiempo límite'):
        super().__init__(message, 408)
