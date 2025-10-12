"""
Sistema de logging centralizado
"""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    Configura el sistema de logging para la aplicación
    
    Args:
        app: Instancia de Flask
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    log_file = app.config['LOG_FILE']
    
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Formato de logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para archivo
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configurar logger de la app
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Desactivar logs de werkzeug en desarrollo
    if app.config['DEBUG']:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_logger(name):
    """
    Obtiene un logger por nombre
    
    Args:
        name: Nombre del módulo
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)
