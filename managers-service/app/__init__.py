import os
from flask import Flask
from .config.database import db


def create_app(config_name=None):
    app = Flask(__name__)

    # Load DB url from environment to allow using the central DB (e.g. Postgres)
    db_url = os.getenv('DATABASE_URL')

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # enable Flask testing mode so decorators can detect test environment
        app.config['TESTING'] = True
    else:
        # prefer environment variable, fallback to a local sqlite file for development
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///managers.db'

    # common SQLAlchemy config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Auth/JWT configuration (read from env; docker-compose provides these)
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')

    db.init_app(app)
    
    # register middleware error handlers
    from app.core.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    with app.app_context():
        # register routes
        from .modules.managers.routes import managers_bp
        app.register_blueprint(managers_bp, url_prefix='/api/v1')
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'managers-service'}, 200

    return app
