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
from app.modules.inventory.product_model import Product
from datetime import date, timedelta


@pytest.fixture(scope='function')
def app():
    """Crea una instancia de la aplicación para tests"""
    app = create_app('testing')
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
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
            categoria="Medicamentos",
            unidad_medida="tableta",
            proveedor="Farmacéutica XYZ",
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
            categoria="Medicamentos",
            unidad_medida="tableta",
            proveedor="Farmacéutica ABC",
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
            categoria="Endocrinología",
            unidad_medida="tableta",
            proveedor="Farmacéutica MNO",
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
            bodega_id=1,
            bodega_nombre="Bodega Principal",
            pasillo="A",
            estanteria="01",
            nivel="1",
            lote="LOT-2024-001",
            fecha_vencimiento=date.today() + timedelta(days=730),
            cantidad=500,
            cantidad_reservada=0,
            cantidad_disponible=500,
            cantidad_minima=100,
            cantidad_maxima=1000,
            status="available"
        ),
        InventoryItem(
            product_id=2,
            bodega_id=1,
            bodega_nombre="Bodega Principal",
            pasillo="A",
            estanteria="02",
            nivel="1",
            lote="LOT-2024-002",
            fecha_vencimiento=date.today() + timedelta(days=700),
            cantidad=300,
            cantidad_reservada=0,
            cantidad_disponible=300,
            cantidad_minima=80,
            cantidad_maxima=800,
            status="available"
        ),
        InventoryItem(
            product_id=3,
            bodega_id=1,
            bodega_nombre="Bodega Principal",
            pasillo="B",
            estanteria="03",
            nivel="2",
            lote="LOT-2024-006",
            fecha_vencimiento=date.today() + timedelta(days=650),
            cantidad=350,
            cantidad_reservada=0,
            cantidad_disponible=350,
            cantidad_minima=80,
            cantidad_maxima=700,
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
