from functools import wraps
from flask import g, current_app
from app.core.auth.jwt_validator import get_token_from_request, verify_token_with_auth_service
from app.core.exceptions import UnauthorizedError, ForbiddenError


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In testing mode, bypass external auth checks and provide a dummy user
        if current_app.config.get('TESTING'):
            g.current_user = {'id': 0, 'username': 'test', 'role': 'tester'}
            g.user_id = 0
            g.username = 'test'
            g.user_role = 'tester'
            return f(*args, **kwargs)

        token = get_token_from_request()
        user_data = verify_token_with_auth_service(token)
        g.current_user = user_data.get('user', {})
        g.user_id = user_data.get('user', {}).get('id')
        g.username = user_data.get('user', {}).get('username')
        g.user_role = user_data.get('user', {}).get('role')
        return f(*args, **kwargs)
    return decorated_function


def require_permission(*roles):
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_role = g.get('user_role')
            if user_role not in roles:
                raise ForbiddenError(f'Role required: {roles}')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = get_token_from_request()
            user_data = verify_token_with_auth_service(token)
            g.current_user = user_data.get('user', {})
            g.user_id = user_data.get('user', {}).get('id')
            g.username = user_data.get('user', {}).get('username')
            g.user_role = user_data.get('user', {}).get('role')
        except Exception:
            g.current_user = None
            g.user_id = None
            g.username = None
            g.user_role = None
        return f(*args, **kwargs)
    return decorated_function