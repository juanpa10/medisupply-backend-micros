"""
Tests para el endpoint de búsqueda por producto

Prueba el endpoint: GET /api/v1/inventory/search-product?q=<query>
"""
import pytest
import json
from unittest.mock import patch, MagicMock


class TestSearchProductEndpoint:
    """Suite de tests para búsqueda por producto"""
    
    def test_search_without_query_parameter(self, client, auth_headers):
        """Test 1: Búsqueda sin parámetro 'q' debe retornar error 400"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product',
                headers=auth_headers
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'término de búsqueda' in data['message'].lower()
    
    def test_search_with_short_query(self, client, auth_headers):
        """Test 2: Query muy corto (< 2 caracteres) debe retornar error 400"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=a',
                headers=auth_headers
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'al menos 2 caracteres' in data['message'].lower()
    
    def test_search_by_product_name(self, client, auth_headers, sample_inventory):
        """Test 3: Búsqueda por nombre de producto debe retornar resultados"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=paracetamol',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verificar estructura de respuesta
            assert data['success'] is True
            assert 'producto(s) encontrado(s)' in data['message']
            assert isinstance(data['data'], list)
            
            # Verificar que encontró el producto
            assert len(data['data']) > 0
            
            # Verificar estructura del primer item
            item = data['data'][0]
            assert 'id' in item
            assert 'product_id' in item
            assert 'pasillo' in item
            assert 'estanteria' in item
            assert 'nivel' in item
            assert 'ubicacion' in item
            assert 'cantidad' in item
            assert 'status' in item
            assert 'created_at' in item
            assert 'updated_at' in item
            assert 'product_info' in item
            
            # Verificar estructura de product_info
            product_info = item['product_info']
            assert 'nombre' in product_info
            assert 'codigo' in product_info
            assert 'referencia' in product_info
            assert 'descripcion' in product_info
            assert 'categoria' in product_info
            assert 'unidad_medida' in product_info
            assert 'proveedor' in product_info
            
            # Verificar valores
            assert product_info['nombre'] == 'Paracetamol 500mg'
            assert product_info['codigo'] == 'MED-001'
            assert item['cantidad'] == 500.0
    
    def test_search_by_product_code(self, client, auth_headers, sample_inventory):
        """Test 4: Búsqueda por código de producto debe retornar resultados"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=MED-001',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert len(data['data']) > 0
            assert data['data'][0]['product_info']['codigo'] == 'MED-001'
    
    def test_search_by_product_reference(self, client, auth_headers, sample_inventory):
        """Test 5: Búsqueda por referencia de producto debe retornar resultados"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=REF-PARA',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert len(data['data']) > 0
            assert 'REF-PARA' in data['data'][0]['product_info']['referencia']
    
    def test_search_case_insensitive(self, client, auth_headers, sample_inventory):
        """Test 6: Búsqueda debe ser case-insensitive"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            # Búsqueda en mayúsculas
            response_upper = client.get(
                '/api/v1/inventory/search-product?q=PARACETAMOL',
                headers=auth_headers
            )
            
            # Búsqueda en minúsculas
            response_lower = client.get(
                '/api/v1/inventory/search-product?q=paracetamol',
                headers=auth_headers
            )
            
            data_upper = json.loads(response_upper.data)
            data_lower = json.loads(response_lower.data)
            
            # Deben retornar la misma cantidad de resultados
            assert len(data_upper['data']) == len(data_lower['data'])
            assert len(data_upper['data']) > 0
    
    def test_search_partial_match(self, client, auth_headers, sample_inventory):
        """Test 7: Búsqueda parcial debe funcionar"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            # Buscar 'metfor' debería encontrar 'Metformina'
            response = client.get(
                '/api/v1/inventory/search-product?q=metfor',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert len(data['data']) > 0
            
            # Verificar que encontró Metformina
            found_metformina = any(
                'metformina' in item['product_info']['nombre'].lower()
                for item in data['data']
            )
            assert found_metformina
    
    def test_search_no_results(self, client, auth_headers, sample_inventory):
        """Test 8: Búsqueda sin resultados debe retornar lista vacía"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=ProductoInexistente123',
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['success'] is True
            assert len(data['data']) == 0
            assert '0 producto(s)' in data['message']
    
    def test_search_response_format(self, client, auth_headers, sample_inventory):
        """Test 9: Verificar formato exacto de respuesta"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=paracetamol',
                headers=auth_headers
            )
            
            data = json.loads(response.data)
            
            # Verificar estructura raíz
            assert 'success' in data
            assert 'message' in data
            assert 'data' in data
            
            # Verificar tipos
            assert isinstance(data['success'], bool)
            assert isinstance(data['message'], str)
            assert isinstance(data['data'], list)
            
            if len(data['data']) > 0:
                item = data['data'][0]
                
                # Verificar campos requeridos
                required_fields = [
                    'id', 'product_id', 'pasillo', 'estanteria', 'nivel',
                    'ubicacion', 'cantidad', 'status', 'created_at', 
                    'updated_at', 'product_info'
                ]
                
                for field in required_fields:
                    assert field in item, f"Campo '{field}' faltante en respuesta"
                
                # Verificar tipos de datos
                assert isinstance(item['id'], int)
                assert isinstance(item['product_id'], int)
                assert isinstance(item['pasillo'], str)
                assert isinstance(item['estanteria'], str)
                assert isinstance(item['nivel'], str)
                assert isinstance(item['ubicacion'], str)
                assert isinstance(item['cantidad'], float)
                assert isinstance(item['status'], str)
                assert isinstance(item['product_info'], dict)
                
                # Verificar campos de product_info
                product_info_fields = [
                    'nombre', 'codigo', 'referencia', 'descripcion',
                    'categoria', 'unidad_medida', 'proveedor'
                ]
                
                for field in product_info_fields:
                    assert field in item['product_info'], \
                        f"Campo '{field}' faltante en product_info"
    
    def test_search_without_authentication(self, client):
        """Test 10: Búsqueda sin autenticación debe retornar error 401"""
        response = client.get('/api/v1/inventory/search-product?q=test')
        
        # Dependiendo de la configuración de auth, puede retornar 401
        # Si el mock no está activo, debería requerir autenticación
        assert response.status_code in [401, 403, 500]
    
    def test_ubicacion_format(self, client, auth_headers, sample_inventory):
        """Test 11: Verificar formato de ubicación"""
        with patch('app.core.auth.jwt_validator.JWTValidator.validate_token') as mock_validate:
            mock_validate.return_value = ({'sub': '1', 'username': 'test_user', 'role': 'operator'}, None)
            
            response = client.get(
                '/api/v1/inventory/search-product?q=paracetamol',
                headers=auth_headers
            )
            
            data = json.loads(response.data)
            
            if len(data['data']) > 0:
                item = data['data'][0]
                ubicacion = item['ubicacion']
                
                # Verificar formato: "Pasillo X - Estantería Y - Nivel Z"
                assert 'Pasillo' in ubicacion
                assert 'Estantería' in ubicacion
                assert 'Nivel' in ubicacion
                assert ' - ' in ubicacion
                
                # Verificar coherencia con campos individuales
                assert item['pasillo'] in ubicacion
                assert item['estanteria'] in ubicacion
                assert item['nivel'] in ubicacion


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
