"""
Inicialización de la aplicación Flask
"""
from flask import Flask
from flask_cors import CORS
from app.config.settings import get_config
from app.config.database import db, migrate
import os
from app.core.middleware.error_handler import register_error_handlers
from app.core.middleware.request_logger import RequestLogger
from app.core.utils.logger import setup_logger


def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Cargar configuración
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Configurar logging
    setup_logger(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Registrar middleware
    RequestLogger(app)
    register_error_handlers(app)
    
    # Registrar blueprints
    with app.app_context():
        from app.modules.inventory.routes import inventory_bp
        from app.modules.products.routes import products_bp
        
        app.register_blueprint(inventory_bp)
        app.register_blueprint(products_bp)

        # Auto-create tables on startup (similar behaviour to video-api)
        # Controlled by env var AUTO_CREATE_TABLES (default: true for local/dev)
        auto_create = os.environ.get('AUTO_CREATE_TABLES', 'true').lower() in ('1', 'true', 'yes')
        if auto_create:
            try:
                db.create_all()
            except Exception:
                # If migrations are preferred or an error occurs, skip silently
                pass
    
    @app.route('/health')
    def health_check():
        """Endpoint de health check"""
        return {'status': 'healthy', 'service': 'inventory-service'}, 200
    
    return app
