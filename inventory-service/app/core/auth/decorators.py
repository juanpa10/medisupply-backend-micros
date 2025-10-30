"""
Decoradores de autenticación y autorización
"""
from functools import wraps
from flask import g, jsonify
from app.core.auth.jwt_validator import JWTValidator
from app.core.utils.response import error_response


def require_auth(f):
    """
    Decorador que requiere autenticación JWT
    
    Usage:
        @require_auth
        def protected_route():
            user = g.user  # Acceder al usuario autenticado
            return {'message': 'Protected'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, error = JWTValidator.validate_token()
        
        if error:
            return error_response(error, 401)
        
        # Guardar información del usuario en el contexto
        g.user = payload.get('sub')
        g.role = payload.get('role')
        g.user_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(*allowed_roles):
    """
    Decorador que requiere roles específicos
    
    Args:
        *allowed_roles: Roles permitidos para acceder al endpoint
        
    Usage:
        @require_permission('admin', 'warehouse_operator')
        def admin_route():
            return {'message': 'Admin only'}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload, error = JWTValidator.validate_token()
            
            if error:
                return error_response(error, 401)
            
            user_role = payload.get('role')
            
            if user_role not in allowed_roles:
                return error_response(
                    f'Acceso denegado. Se requiere uno de los siguientes roles: {", ".join(allowed_roles)}',
                    403
                )
            
            # Guardar información del usuario en el contexto
            g.user = payload.get('sub')
            g.role = user_role
            g.user_payload = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def optional_auth(f):
    """
    Decorador que permite acceso con o sin autenticación
    Si hay token, se valida y se guarda en g.user
    Si no hay token, se permite el acceso igualmente
    
    Usage:
        @optional_auth
        def public_route():
            if hasattr(g, 'user'):
                return {'message': f'Hello {g.user}'}
            return {'message': 'Hello anonymous'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, error = JWTValidator.validate_token()
        
        if not error and payload:
            g.user = payload.get('sub')
            g.role = payload.get('role')
            g.user_payload = payload
        
        return f(*args, **kwargs)
    
    return decorated_function
