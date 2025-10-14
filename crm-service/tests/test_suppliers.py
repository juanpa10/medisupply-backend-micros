"""
Tests para el módulo de Suppliers
"""
import pytest
import io
from app.modules.suppliers.models import Supplier


class TestSupplierEndpoints:
    """Tests para endpoints de proveedores"""
    
    def test_health_check(self, client):
        """Test del endpoint de health check"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_create_supplier_without_auth(self, client):
        """Test crear proveedor sin autenticación"""
        response = client.post('/api/v1/suppliers')
        assert response.status_code == 401
    
    def test_get_suppliers_list(self, client, auth_headers, db):
        """Test obtener lista de proveedores"""
        # Aquí normalmente harías el request con autenticación válida
        # response = client.get('/api/v1/suppliers', headers=auth_headers)
        # assert response.status_code == 200
        pass
    
    def test_supplier_model_creation(self, db):
        """Test creación de modelo Supplier"""
        supplier = Supplier(
            razon_social='Test Company',
            nit='123456789',
            representante_legal='John Doe',
            pais='Colombia',
            nombre_contacto='Jane Doe',
            celular_contacto='1234567890',
            certificado_filename='cert.pdf',
            certificado_path='/tmp/cert.pdf',
            created_by='test_user'
        )
        db.session.add(supplier)
        db.session.commit()
        
        assert supplier.id is not None
        assert supplier.razon_social == 'Test Company'
        assert supplier.nit == '123456789'
        assert supplier.is_deleted is False


class TestSupplierValidations:
    """Tests para validaciones de proveedores"""
    
    def test_nit_uniqueness(self, db):
        """Test que el NIT debe ser único"""
        supplier1 = Supplier(
            razon_social='Company 1',
            nit='123456789',
            representante_legal='John Doe',
            pais='Colombia',
            nombre_contacto='Jane Doe',
            celular_contacto='1234567890',
            certificado_filename='cert1.pdf',
            certificado_path='/tmp/cert1.pdf'
        )
        db.session.add(supplier1)
        db.session.commit()
        
        supplier2 = Supplier(
            razon_social='Company 2',
            nit='123456789',  # Mismo NIT
            representante_legal='Jane Doe',
            pais='México',
            nombre_contacto='John Doe',
            celular_contacto='9876543210',
            certificado_filename='cert2.pdf',
            certificado_path='/tmp/cert2.pdf'
        )
        db.session.add(supplier2)
        
        with pytest.raises(Exception):  # Debería lanzar IntegrityError
            db.session.commit()
