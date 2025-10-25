"""
Validador de tokens JWT
"""
import jwt
import requests
from functools import wraps
from flask import current_app, request
from typing import Dict, Optional


class JWTValidator:
    """Validador de tokens JWT"""
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """
        Decodifica un token JWT
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Payload del token decodificado
            
        Raises:
            jwt.ExpiredSignatureError: Token expirado
            jwt.InvalidTokenError: Token inválido
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError('Token expirado')
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError('Token inválido')
    
    @staticmethod
    def verify_with_auth_service(token: str) -> Optional[Dict]:
        """
        Verifica el token con el servicio de autenticación
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Información del usuario si es válido, None si no
        """
        try:
            auth_url = current_app.config['AUTH_SERVICE_URL']
            response = requests.get(
                f"{auth_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return {
                        'sub': data.get('sub'),
                        'role': data.get('role')
                    }
            return None
        except Exception as e:
            current_app.logger.error(f"Error verificando token con auth service: {str(e)}")
            return None
    
    @staticmethod
    def extract_token_from_request() -> Optional[str]:
        """
        Extrae el token del header Authorization
        
        Returns:
            Token JWT si existe, None si no
        """
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    @staticmethod
    def validate_token() -> tuple[Optional[Dict], Optional[str]]:
        """
        Valida el token de la petición actual
        
        Returns:
            Tupla (payload, error_message)
        """
        token = JWTValidator.extract_token_from_request()
        
        if not token:
            return None, 'Token no proporcionado'
        
        try:
            # Primero intentar decodificar localmente
            payload = JWTValidator.decode_token(token)
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token expirado'
        except jwt.InvalidTokenError:
            # Si falla, intentar con el servicio de auth
            payload = JWTValidator.verify_with_auth_service(token)
            if payload:
                return payload, None
            return None, 'Token inválido'
