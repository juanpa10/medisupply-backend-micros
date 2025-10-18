import jwt
import requests
from flask import request, current_app
from app.core.exceptions import UnauthorizedError


def validate_jwt_token(token):
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('JWT_SECRET') or current_app.config.get('JWT_SECRET_KEY'),
            algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError('Token expired')
    except jwt.InvalidTokenError:
        raise UnauthorizedError('Invalid token')


def verify_token_with_auth_service(token):
    try:
        auth_url = current_app.config.get('AUTH_SERVICE_URL')
        if auth_url:
            verify_url = auth_url.rstrip('/') + '/auth/verify'
            response = requests.get(verify_url, headers={'Authorization': f'Bearer {token}'}, timeout=5)
            if response.status_code == 200:
                return response.json()
        # fallback to local
        return validate_jwt_token(token)
    except requests.RequestException:
        return validate_jwt_token(token)


def get_token_from_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise UnauthorizedError('Authorization token required')
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise UnauthorizedError('Invalid auth scheme')
        return token
    except ValueError:
        raise UnauthorizedError('Invalid token format')