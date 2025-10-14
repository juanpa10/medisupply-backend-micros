"""
Validador de tokens JWT
"""
import jwt
import requests
from functools import wraps
from flask import request, current_app, g
from app.core.exceptions import UnauthorizedError


def validate_jwt_token(token):
    """
    Valida un token JWT
    
    Args:
        token: Token JWT a validar
        
    Returns:
        dict: Datos decodificados del token
        
    Raises:
        UnauthorizedError: Si el token es inválido
    """
    try:
        # Decodificar token
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError('Token expirado')
    except jwt.InvalidTokenError:
        raise UnauthorizedError('Token inválido')


def verify_token_with_auth_service(token):
    """
    Verifica el token con el servicio de autenticación
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        dict: Información del usuario
        
    Raises:
        UnauthorizedError: Si el token es inválido
    """
    try:
        auth_url = current_app.config['AUTH_SERVICE_URL'].rstrip('/')
        # auth-service exposes /auth/verify (not /api/v1/auth/verify)
        verify_url = f"{auth_url}/auth/verify"
        response = requests.get(
            verify_url,
            headers={'Authorization': f'Bearer {token}'},
            timeout=5
        )

        if response.status_code == 200:
            return response.json()
        else:
            # If auth service returns non-200, try a local validation as fallback
            try:
                return validate_jwt_token(token)
            except Exception:
                raise UnauthorizedError('Token inválido')
    except requests.RequestException:
        # Si el servicio de auth no está disponible, validar localmente
        return validate_jwt_token(token)


def get_token_from_request():
    """
    Extrae el token del header Authorization
    
    Returns:
        str: Token JWT
        
    Raises:
        UnauthorizedError: Si no se encuentra el token
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise UnauthorizedError('Token de autenticación requerido')
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise UnauthorizedError('Esquema de autenticación inválido')
        return token
    except ValueError:
        raise UnauthorizedError('Formato de token inválido')
