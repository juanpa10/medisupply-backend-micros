"""
Configuración de la aplicación
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/inventory_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET = os.environ.get('JWT_SECRET', 'your-super-secret-jwt-key')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Auth Service
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:9001')
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/inventory-service.log')
    
    # Search Performance
    SEARCH_TIMEOUT = float(os.environ.get('SEARCH_TIMEOUT', '1.0'))
    MAX_RESULTS_PER_PAGE = int(os.environ.get('MAX_RESULTS_PER_PAGE', '100'))
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', '20'))
    
    # Cache (opcional)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_ENABLED = os.environ.get('CACHE_ENABLED', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False  # Cambiar a True para ver queries SQL


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Requerir variables de entorno en producción
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Validar que existan variables críticas
        assert os.environ.get('DATABASE_URL'), 'DATABASE_URL must be set'
        assert os.environ.get('JWT_SECRET'), 'JWT_SECRET must be set'


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    
    # Base de datos en memoria para tests (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Deshabilitar CSRF para tests
    WTF_CSRF_ENABLED = False
    
    # Timeout más alto para tests
    SEARCH_TIMEOUT = 5.0


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Obtener configuración según el entorno"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
