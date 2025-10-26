"""Tests para pagination.py para mejorar cobertura"""
import pytest
from app.core.utils.pagination import get_pagination_params, paginate_query


class TestPaginationParams:
    """Tests para get_pagination_params"""
    
    def test_get_pagination_with_page_less_than_1(self, app):
        """Test que page < 1 se ajusta a 1"""
        with app.test_request_context('/?page=0&per_page=10'):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == 10
    
    def test_get_pagination_with_negative_page(self, app):
        """Test que page negativo se ajusta a 1"""
        with app.test_request_context('/?page=-5&per_page=10'):
            page, per_page = get_pagination_params()
            assert page == 1
    
    def test_get_pagination_with_per_page_greater_than_max(self, app):
        """Test que per_page > MAX se ajusta al máximo"""
        # MAX_PAGE_SIZE es 100 por defecto
        with app.test_request_context('/?page=1&per_page=500'):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == app.config['MAX_PAGE_SIZE']
            assert per_page == 100
    
    def test_get_pagination_with_per_page_less_than_1(self, app):
        """Test que per_page < 1 se ajusta al default"""
        with app.test_request_context('/?page=1&per_page=0'):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == app.config['DEFAULT_PAGE_SIZE']
    
    def test_get_pagination_with_negative_per_page(self, app):
        """Test que per_page negativo se ajusta al default"""
        with app.test_request_context('/?page=1&per_page=-10'):
            page, per_page = get_pagination_params()
            assert per_page == app.config['DEFAULT_PAGE_SIZE']
    
    def test_get_pagination_defaults(self, app):
        """Test valores por defecto sin parámetros"""
        with app.test_request_context('/'):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == app.config['DEFAULT_PAGE_SIZE']


class TestPaginateQuery:
    """Tests para paginate_query"""
    
    def test_paginate_query_with_explicit_params(self, app, db):
        """Test paginación con parámetros explícitos"""
        from app.modules.suppliers.models import Supplier
        
        with app.app_context():
            # Crear algunos proveedores de prueba
            for i in range(15):
                s = Supplier(
                    razon_social=f'Supplier {i}',
                    nit=f'NIT-{i}',
                    representante_legal='Rep',
                    pais='Colombia',
                    nombre_contacto='Contact',
                    celular_contacto='123456',
                    certificado_filename='cert.pdf',
                    certificado_path='/path/cert.pdf'
                )
                db.session.add(s)
            db.session.commit()
            
            # Paginar
            query = Supplier.query
            result = paginate_query(query, page=2, per_page=5)
            
            assert result['total'] == 15
            assert result['page'] == 2
            assert result['per_page'] == 5
            assert len(result['items']) == 5
    
    def test_paginate_query_uses_request_params(self, app, db):
        """Test que paginate_query usa parámetros del request si no se proporcionan"""
        from app.modules.suppliers.models import Supplier
        
        with app.app_context():
            # Crear algunos proveedores
            for i in range(10):
                s = Supplier(
                    razon_social=f'Supplier {i}',
                    nit=f'NIT-REQ-{i}',
                    representante_legal='Rep',
                    pais='Colombia',
                    nombre_contacto='Contact',
                    celular_contacto='123456',
                    certificado_filename='cert.pdf',
                    certificado_path='/path/cert.pdf'
                )
                db.session.add(s)
            db.session.commit()
            
            # Usar request context con parámetros
            with app.test_request_context('/?page=1&per_page=3'):
                query = Supplier.query.filter_by(is_deleted=False)
                result = paginate_query(query, page=None, per_page=None)
                
                assert result['page'] == 1
                assert result['per_page'] == 3
