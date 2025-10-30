from flask import Flask
from flask_restx import Api
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///reports_test.db')
    api = Api(app, title='Reports Service', version='1.0', doc='/docs')

    # register namespaces
    from app.controllers.api import ns as reports_ns
    api.add_namespace(reports_ns, path='/api/v1')

    # health
    @app.route('/health')
    def health():
        return {'status': 'ok'}

    # init DB at startup if requested
    if os.getenv('INIT_DB', 'false').lower() in ('1', 'true', 'yes'):
        from init_db import init_db
        try:
            init_db(app.config['SQLALCHEMY_DATABASE_URI'])
            print('✅ Reports DB initialized')
        except Exception as e:
            print('DB init error:', e)

    return app
