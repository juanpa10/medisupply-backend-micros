"""
Manejo global de errores
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.core.exceptions import AppException
from app.core.utils.response import error_response
from app.core.utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    """Registra los manejadores de errores globales"""
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Maneja excepciones de la aplicación"""
        logger.error(f'AppException: {error.message}', exc_info=True)
        return error_response(
            message=error.message,
            status_code=error.status_code,
            errors=error.payload
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Maneja excepciones HTTP de Werkzeug"""
        logger.error(f'HTTPException: {error.description}', exc_info=True)
        return error_response(
            message=error.description,
            status_code=error.code
        )
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Maneja errores de valor"""
        logger.error(f'ValueError: {str(error)}', exc_info=True)
        return error_response(
            message=str(error),
            status_code=400
        )
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Maneja excepciones genéricas"""
        logger.exception('Unhandled exception', exc_info=True)
        return error_response(
            message='Error interno del servidor',
            status_code=500
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Maneja error 404"""
        return error_response(
            message='Endpoint no encontrado',
            status_code=404
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Maneja error 405"""
        return error_response(
            message='Método no permitido',
            status_code=405
        )
