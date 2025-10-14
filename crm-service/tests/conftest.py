"""
Configuración de fixtures para pytest
"""
import os
import pytest
from app import create_app
from app.config.database import db as _db


@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la aplicación para testing"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """Crea una base de datos temporal para testing"""
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Crea un cliente de prueba"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Headers de autenticación para testing"""
    # Token de prueba (deberías generar uno válido para tus tests)
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'multipart/form-data'
    }
