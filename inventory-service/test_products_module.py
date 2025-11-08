"""
Tests básicos para el módulo de productos

Verifica que la funcionalidad de creación de productos funcione correctamente.
"""
import pytest
import sys
from pathlib import Path
from io import BytesIO

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app import create_app
from app.config.database import db
from app.modules.products.models import Product, Categoria, UnidadMedida, Proveedor
from app.modules.products.service import ProductService, CategoriaService, UnidadMedidaService, ProveedorService


class TestProductModule:
    """Tests para el módulo de productos"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Crear datos maestros básicos
            self._create_master_data()
    
    def _create_master_data(self):
        """Crea datos maestros para tests"""
        # Crear categoría
        categoria = Categoria(nombre='Test Categoria', descripcion='Categoría de prueba')
        db.session.add(categoria)
        
        # Crear unidad de medida
        unidad = UnidadMedida(nombre='Test Unidad', abreviatura='TU', descripcion='Unidad de prueba')
        db.session.add(unidad)
        
        # Crear proveedor
        proveedor = Proveedor(nombre='Test Proveedor', nit='123456789')
        db.session.add(proveedor)
        
        db.session.commit()
        
        self.categoria_id = categoria.id
        self.unidad_id = unidad.id
        self.proveedor_id = proveedor.id
    
    def test_create_categoria_service(self):
        """Test crear categoría via service"""
        with self.app.app_context():
            service = CategoriaService()
            
            categoria_data = {
                'nombre': 'Nueva Categoria',
                'descripcion': 'Descripción de prueba'
            }
            
            categoria = service.create_categoria(categoria_data, 'test_user')
            
            assert categoria.id is not None
            assert categoria.nombre == 'Nueva Categoria'
            assert categoria.created_by == 'test_user'
    
    def test_create_unidad_medida_service(self):
        """Test crear unidad de medida via service"""
        with self.app.app_context():
            service = UnidadMedidaService()
            
            unidad_data = {
                'nombre': 'Kilogramo',
                'abreviatura': 'KG',
                'descripcion': 'Unidad de peso'
            }
            
            unidad = service.create_unidad_medida(unidad_data, 'test_user')
            
            assert unidad.id is not None
            assert unidad.nombre == 'Kilogramo'
            assert unidad.abreviatura == 'KG'
    
    def test_create_proveedor_service(self):
        """Test crear proveedor via service"""
        with self.app.app_context():
            service = ProveedorService()
            
            proveedor_data = {
                'nombre': 'Nuevo Proveedor',
                'nit': '987654321',
                'contacto_email': 'test@proveedor.com'
            }
            
            proveedor = service.create_proveedor(proveedor_data, 'test_user')
            
            assert proveedor.id is not None
            assert proveedor.nombre == 'Nuevo Proveedor'
            assert proveedor.nit == '987654321'
    
    def test_create_product_service(self):
        """Test crear producto via service"""
        with self.app.app_context():
            service = ProductService()
            
            product_data = {
                'nombre': 'Producto de Prueba',
                'codigo': 'TEST-001',
                'descripcion': 'Producto para testing unitario del sistema',
                'categoria_id': self.categoria_id,
                'unidad_medida_id': self.unidad_id,
                'proveedor_id': self.proveedor_id,
                'precio_compra': 10.00,
                'precio_venta': 15.00
            }
            
            product = service.create_product(product_data, current_user='test_user')
            
            assert product.id is not None
            assert product.nombre == 'Producto de Prueba'
            assert product.codigo == 'TEST-001'
            assert product.created_by == 'test_user'
            assert product.categoria_id == self.categoria_id
            assert product.unidad_medida_id == self.unidad_id
            assert product.proveedor_id == self.proveedor_id
    
    def test_product_catalog_status(self):
        """Test estado del producto en catálogo"""
        with self.app.app_context():
            service = ProductService()
            
            # Producto que requiere todos los documentos
            product_data = {
                'nombre': 'Producto Completo',
                'codigo': 'COMP-001',
                'descripcion': 'Producto que requiere documentos completos',
                'categoria_id': self.categoria_id,
                'unidad_medida_id': self.unidad_id,
                'proveedor_id': self.proveedor_id,
                'requiere_ficha_tecnica': True,
                'requiere_condiciones_almacenamiento': True,
                'requiere_certificaciones_sanitarias': True
            }
            
            product = service.create_product(product_data)
            catalog_status = service.get_product_catalog_status(product.id)
            
            # Debe estar pendiente de documentos
            assert catalog_status['catalog_status'] == 'pending_documents'
            assert catalog_status['has_required_documents'] == False
            
            # Producto que no requiere documentos
            product_data_no_docs = {
                'nombre': 'Producto Simple',
                'codigo': 'SIMP-001',
                'descripcion': 'Producto que no requiere documentos',
                'categoria_id': self.categoria_id,
                'unidad_medida_id': self.unidad_id,
                'proveedor_id': self.proveedor_id,
                'requiere_ficha_tecnica': False,
                'requiere_condiciones_almacenamiento': False,
                'requiere_certificaciones_sanitarias': False
            }
            
            product_simple = service.create_product(product_data_no_docs)
            catalog_status_simple = service.get_product_catalog_status(product_simple.id)
            
            # Debe estar disponible
            assert catalog_status_simple['catalog_status'] == 'available'
            assert catalog_status_simple['has_required_documents'] == True
    
    def test_search_products(self):
        """Test búsqueda de productos"""
        with self.app.app_context():
            service = ProductService()
            
            # Crear algunos productos
            products_data = [
                {
                    'nombre': 'Paracetamol 500mg',
                    'codigo': 'PARA-500',
                    'descripcion': 'Analgésico para dolor',
                    'categoria_id': self.categoria_id,
                    'unidad_medida_id': self.unidad_id,
                    'proveedor_id': self.proveedor_id
                },
                {
                    'nombre': 'Ibuprofeno 400mg',
                    'codigo': 'IBU-400',
                    'descripcion': 'Antiinflamatorio para dolor',
                    'categoria_id': self.categoria_id,
                    'unidad_medida_id': self.unidad_id,
                    'proveedor_id': self.proveedor_id
                }
            ]
            
            for prod_data in products_data:
                service.create_product(prod_data)
            
            # Buscar por término
            results, total, metadata = service.search_products(search_term='para')
            assert total >= 1
            assert any('para' in p.nombre.lower() or 'para' in p.codigo.lower() for p in results)
            
            # Buscar por categoría
            results_cat, total_cat, _ = service.search_products(categoria_id=self.categoria_id)
            assert total_cat >= 2
    
    def test_duplicate_codigo_validation(self):
        """Test validación de código duplicado"""
        with self.app.app_context():
            service = ProductService()
            
            product_data = {
                'nombre': 'Primer Producto',
                'codigo': 'DUP-001',
                'descripcion': 'Primer producto con código duplicado',
                'categoria_id': self.categoria_id,
                'unidad_medida_id': self.unidad_id,
                'proveedor_id': self.proveedor_id
            }
            
            # Crear primer producto
            service.create_product(product_data)
            
            # Intentar crear segundo producto con mismo código
            product_data_dup = product_data.copy()
            product_data_dup['nombre'] = 'Segundo Producto'
            
            with pytest.raises(Exception) as exc_info:
                service.create_product(product_data_dup)
            
            assert 'código' in str(exc_info.value).lower()
    
    def test_invalid_foreign_keys(self):
        """Test validación de foreign keys inválidas"""
        with self.app.app_context():
            service = ProductService()
            
            product_data = {
                'nombre': 'Producto Inválido',
                'codigo': 'INV-001',
                'descripcion': 'Producto con FK inválidas',
                'categoria_id': 99999,  # ID que no existe
                'unidad_medida_id': self.unidad_id,
                'proveedor_id': self.proveedor_id
            }
            
            with pytest.raises(Exception) as exc_info:
                service.create_product(product_data)
            
            assert 'categoría' in str(exc_info.value).lower() or 'encontrada' in str(exc_info.value).lower()


def run_basic_tests():
    """Ejecuta tests básicos sin pytest"""
    print("🧪 Ejecutando tests básicos del módulo de productos...")
    
    app = create_app('testing')
    
    with app.app_context():
        try:
            db.create_all()
            
            # Test 1: Crear datos maestros
            print("  🔍 Test 1: Creación de datos maestros...")
            categoria_service = CategoriaService()
            unidad_service = UnidadMedidaService()
            proveedor_service = ProveedorService()
            
            categoria = categoria_service.create_categoria({'nombre': 'Test Cat'}, 'test')
            unidad = unidad_service.create_unidad_medida({'nombre': 'Test Unit', 'abreviatura': 'TU'}, 'test')
            proveedor = proveedor_service.create_proveedor({'nombre': 'Test Prov'}, 'test')
            
            assert categoria.id is not None
            assert unidad.id is not None
            assert proveedor.id is not None
            print("    ✅ Datos maestros creados correctamente")
            
            # Test 2: Crear producto
            print("  🔍 Test 2: Creación de producto...")
            product_service = ProductService()
            
            product_data = {
                'nombre': 'Test Product',
                'codigo': 'TEST-001',
                'descripcion': 'Producto de prueba para validar funcionamiento básico',
                'categoria_id': categoria.id,
                'unidad_medida_id': unidad.id,
                'proveedor_id': proveedor.id,
                'precio_venta': 10.00
            }
            
            product = product_service.create_product(product_data, current_user='test')
            assert product.id is not None
            assert product.codigo == 'TEST-001'
            print("    ✅ Producto creado correctamente")
            
            # Test 3: Estado del catálogo
            print("  🔍 Test 3: Estado del catálogo...")
            catalog_status = product_service.get_product_catalog_status(product.id)
            assert 'catalog_status' in catalog_status
            print(f"    ✅ Estado del catálogo: {catalog_status['catalog_status']}")
            
            # Test 4: Búsqueda
            print("  🔍 Test 4: Búsqueda de productos...")
            results, total, metadata = product_service.search_products(search_term='test')
            assert total >= 1
            print(f"    ✅ Búsqueda exitosa: {total} productos encontrados")
            
            print("\n🎉 ¡Todos los tests básicos pasaron exitosamente!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error en tests: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = run_basic_tests()
    if not success:
        sys.exit(1)