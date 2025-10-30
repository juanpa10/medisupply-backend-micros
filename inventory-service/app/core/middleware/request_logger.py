"""
Logging de requests HTTP
"""
import time
from flask import request, g
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLogger:
    """Middleware para logging de requests"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa el middleware con la app Flask"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    @staticmethod
    def before_request():
        """Se ejecuta antes de cada request"""
        g.start_time = time.time()
        
        # Log de request entrante
        logger.info(
            f'Request: {request.method} {request.path}',
            extra={
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.user_agent.string
            }
        )
    
    @staticmethod
    def after_request(response):
        """Se ejecuta después de cada request"""
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            
            # Log de response
            logger.info(
                f'Response: {request.method} {request.path} - '
                f'{response.status_code} ({elapsed:.3f}s)',
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'elapsed_time': f'{elapsed:.3f}s',
                    'user': g.get('user'),
                    'role': g.get('role')
                }
            )
        
        return response
