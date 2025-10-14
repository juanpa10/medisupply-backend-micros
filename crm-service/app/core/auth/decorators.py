"""
Decoradores de autenticación y autorización
"""
from functools import wraps
from flask import g
from app.core.auth.jwt_validator import get_token_from_request, verify_token_with_auth_service
from app.core.exceptions import UnauthorizedError, ForbiddenError


def require_auth(f):
    """
    Decorador que requiere autenticación
    
    Usage:
        @require_auth
        def my_endpoint():
            user = g.current_user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        user_data = verify_token_with_auth_service(token)
        
        # Almacenar usuario en contexto de Flask
        g.current_user = user_data.get('user', {})
        g.user_id = user_data.get('user', {}).get('id')
        g.username = user_data.get('user', {}).get('username')
        g.user_role = user_data.get('user', {}).get('role')
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(*roles):
    """
    Decorador que requiere permisos específicos
    
    Args:
        roles: Roles permitidos
        
    Usage:
        @require_permission('admin', 'manager')
        def admin_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_role = g.get('user_role')
            
            if user_role not in roles:
                raise ForbiddenError(
                    f'Se requiere uno de los siguientes roles: {", ".join(roles)}'
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def optional_auth(f):
    """
    Decorador que permite autenticación opcional
    Si hay token, lo valida. Si no, continúa sin usuario.
    
    Usage:
        @optional_auth
        def public_endpoint():
            if g.get('current_user'):
                # Usuario autenticado
            else:
                # Usuario anónimo
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = get_token_from_request()
            user_data = verify_token_with_auth_service(token)
            g.current_user = user_data.get('user', {})
            g.user_id = user_data.get('user', {}).get('id')
            g.username = user_data.get('user', {}).get('username')
            g.user_role = user_data.get('user', {}).get('role')
        except UnauthorizedError:
            g.current_user = None
            g.user_id = None
            g.username = None
            g.user_role = None
        
        return f(*args, **kwargs)
    
    return decorated_function
