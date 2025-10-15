from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.core.exceptions import AppException
from app.core.utils.response import error_response
import logging
import traceback


def register_error_handlers(app):

    @app.errorhandler(AppException)
    def handle_app_exception(error):
        return error_response(message=error.message, status_code=error.status_code, errors=error.payload)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return error_response(message=error.description, status_code=error.code)

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return error_response(message=str(error), status_code=400)

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # Log full traceback so container logs include the stacktrace
        logger = logging.getLogger('managers-service')
        logger.exception('Unhandled exception')
        try:
            tb = traceback.format_exc()
            logger.error(tb)
        except Exception:
            pass
        return error_response(message='Error interno del servidor', status_code=500)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response(message='Endpoint no encontrado', status_code=404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return error_response(message='Método no permitido', status_code=405)
