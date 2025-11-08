"""
Configuración de pytest y fixtures para tests
"""
import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app import create_app
from app.config.database import db
from app.modules.inventory.models import InventoryItem
from app.modules.products.models import Product, Categoria, UnidadMedida, Proveedor
from sqlalchemy import Column, Integer, String
from datetime import date, timedelta


# Ya no necesitamos modelos mock porque usamos los reales de app.modules.products.models


@pytest.fixture(scope='function')
def app():
    """Crea una instancia de la aplicación para tests"""
    app = create_app('testing')
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear datos de referencia necesarios para los Foreign Keys
        # Categorías
        categorias = [
            Categoria(id=1, nombre="Medicamentos"),
            Categoria(id=4, nombre="Antidiabéticos")
        ]
        db.session.bulk_save_objects(categorias)
        
        # Unidades de medida
        unidades = [
            UnidadMedida(id=1, nombre="Unidad", abreviatura="UND")
        ]
        db.session.bulk_save_objects(unidades)
        
        # Proveedores
        proveedores = [
            Proveedor(id=1, nombre="Proveedor 1"),
            Proveedor(id=2, nombre="Proveedor 2"),
            Proveedor(id=6, nombre="Proveedor 6")
        ]
        db.session.bulk_save_objects(proveedores)
        
        db.session.commit()
        
        yield app
        
        # Limpiar después de cada test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de test para hacer requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos para tests"""
    with app.app_context():
        yield db.session
        
        # Limpiar después del test
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def sample_products(db_session):
    """Crea productos de muestra para tests"""
    products = [
        Product(
            id=1,
            nombre="Paracetamol 500mg",
            codigo="MED-001",
            referencia="REF-PARA-500",
            descripcion="Analgésico y antipirético",
            categoria_id=1,
            unidad_medida_id=1,
            proveedor_id=1,
            precio_compra=0.50,
            precio_venta=1.20,
            status="active",
            is_deleted=False
        ),
        Product(
            id=2,
            nombre="Ibuprofeno 400mg",
            codigo="MED-002",
            referencia="REF-IBU-400",
            descripcion="Antiinflamatorio no esteroideo",
            categoria_id=1,
            unidad_medida_id=1,
            proveedor_id=2,
            precio_compra=0.60,
            precio_venta=1.50,
            status="active",
            is_deleted=False
        ),
        Product(
            id=3,
            nombre="Metformina 850mg",
            codigo="MED-006",
            referencia="REF-MET-850",
            descripcion="Antidiabético oral",
            categoria_id=4,
            unidad_medida_id=1,
            proveedor_id=6,
            precio_compra=0.40,
            precio_venta=1.00,
            status="active",
            is_deleted=False
        ),
    ]
    
    db_session.bulk_save_objects(products)
    db_session.commit()
    
    return products


@pytest.fixture
def sample_inventory(db_session, sample_products):
    """Crea items de inventario de muestra para tests"""
    items = [
        InventoryItem(
            product_id=1,
            pasillo="A",
            estanteria="01",
            nivel="1",
            cantidad=500,
            status="available"
        ),
        InventoryItem(
            product_id=2,
            pasillo="A",
            estanteria="02",
            nivel="1",
            cantidad=300,
            status="available"
        ),
        InventoryItem(
            product_id=3,
            pasillo="B",
            estanteria="03",
            nivel="2",
            cantidad=350,
            status="available"
        ),
    ]
    
    db_session.bulk_save_objects(items)
    db_session.commit()
    
    return items


@pytest.fixture
def auth_headers():
    """Headers de autenticación simulados"""
    # En un entorno de test real, aquí generarías un token JWT válido
    return {
        'Authorization': 'Bearer test_token_123'
    }
