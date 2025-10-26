"""Tests extendidos para error_handler - alcanzar 90% de cobertura"""
import pytest
from flask import Flask
from app.core.middleware.error_handler import register_error_handlers
from app.core.exceptions import (
    ValidationError, 
    NotFoundError, 
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    FileUploadError
)


@pytest.fixture
def clean_app():
    """Crea una aplicación limpia para cada test"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    register_error_handlers(app)
    return app


class TestErrorHandlerExtended:
    """Tests para todos los manejadores de errores"""
    
    def test_handle_validation_error(self, clean_app):
        """Test manejador de ValidationError"""
        @clean_app.route('/test-validation')
        def test_route():
            raise ValidationError("Campo inválido")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-validation')
            assert resp.status_code == 400
            data = resp.get_json()
            assert data['success'] == False
            assert 'Campo inválido' in data['message']
    
    def test_handle_not_found_error(self, clean_app):
        """Test manejador de NotFoundError"""
        @clean_app.route('/test-notfound')
        def test_route():
            raise NotFoundError("Recurso no encontrado")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-notfound')
            assert resp.status_code == 404
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_conflict_error(self, clean_app):
        """Test manejador de ConflictError"""
        @clean_app.route('/test-conflict')
        def test_route():
            raise ConflictError("Registro duplicado")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-conflict')
            assert resp.status_code == 409
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_unauthorized_error(self, clean_app):
        """Test manejador de UnauthorizedError"""
        @clean_app.route('/test-unauthorized')
        def test_route():
            raise UnauthorizedError("Token inválido")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-unauthorized')
            assert resp.status_code == 401
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_forbidden_error(self, clean_app):
        """Test manejador de ForbiddenError"""
        @clean_app.route('/test-forbidden')
        def test_route():
            raise ForbiddenError("Acceso denegado")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-forbidden')
            assert resp.status_code == 403
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_file_upload_error(self, clean_app):
        """Test manejador de FileUploadError"""
        @clean_app.route('/test-fileupload')
        def test_route():
            raise FileUploadError("Archivo demasiado grande")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-fileupload')
            assert resp.status_code == 400
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_value_error(self, clean_app):
        """Test manejador de ValueError"""
        @clean_app.route('/test-value')
        def test_route():
            raise ValueError("Valor inválido")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-value')
            assert resp.status_code == 400
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_generic_exception(self, clean_app):
        """Test manejador de excepciones genéricas"""
        @clean_app.route('/test-generic')
        def test_route():
            raise RuntimeError("Error inesperado")
        
        with clean_app.test_client() as client:
            resp = client.get('/test-generic')
            assert resp.status_code == 500
            data = resp.get_json()
            assert data['success'] == False
    
    def test_handle_404_not_found_route(self, clean_app):
        """Test para ruta no existente (404 nativo de Flask)"""
        with clean_app.test_client() as client:
            resp = client.get('/ruta-que-no-existe-987654321')
            assert resp.status_code == 404
    
    def test_handle_405_method_not_allowed(self, clean_app):
        """Test para método no permitido"""
        @clean_app.route('/test-post-only', methods=['POST'])
        def test_route():
            return "OK"
        
        with clean_app.test_client() as client:
            resp = client.get('/test-post-only')
            assert resp.status_code == 405
            data = resp.get_json()
            assert data['success'] == False
