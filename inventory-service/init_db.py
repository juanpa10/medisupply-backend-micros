"""
Script de inicialización de la base de datos para Inventory Service

Este script:
1. Elimina y recrea todas las tablas
2. Crea items de inventario de muestra con ubicaciones en bodega
3. Los product_id hacen referencia a productos que existen en products-service

IMPORTANTE: Este es el servicio de INVENTARIO (stock + ubicación).
Los datos del producto (nombre, descripción, etc.) están en products-service.
"""
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app import create_app
from app.config.database import db
from app.modules.inventory.models import InventoryItem, InventoryMovement
from app.modules.inventory.product_model import Product
from app.shared.enums import InventoryStatus, MovementType


def drop_all_tables():
    """Elimina todas las tablas de la base de datos"""
    print("🗑️  Eliminando tablas existentes...")
    db.drop_all()
    print("✅ Tablas eliminadas")


def create_all_tables():
    """Crea todas las tablas definidas en los modelos"""
    print("📦 Creando tablas...")
    db.create_all()
    print("✅ Tablas creadas")


def create_sample_products():
    """
    Crea productos de muestra en la tabla products
    
    NOTA: Normalmente estos productos se crean desde products-service.
    Aquí los creamos solo para propósitos de testing y demostración.
    Los campos categoria_id, unidad_medida_id y proveedor_id son Foreign Keys.
    """
    print("🏷️  Creando productos de muestra...")
    
    products = [
        Product(
            nombre="Paracetamol 500mg",
            codigo="MED-001",
            referencia="REF-PARA-500",
            descripcion="Analgésico y antipirético",
            categoria_id=1,  # Medicamentos
            unidad_medida_id=1,  # tableta
            proveedor_id=1,  # Farmacéutica XYZ
            precio_compra=0.50,
            precio_venta=1.20,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Ibuprofeno 400mg",
            codigo="MED-002",
            referencia="REF-IBU-400",
            descripcion="Antiinflamatorio no esteroideo",
            categoria_id=1,  # Medicamentos
            unidad_medida_id=1,  # tableta
            proveedor_id=2,  # Farmacéutica ABC
            precio_compra=0.60,
            precio_venta=1.50,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Amoxicilina 500mg",
            codigo="MED-003",
            referencia="REF-AMO-500",
            descripcion="Antibiótico de amplio espectro",
            categoria_id=2,  # Antibióticos
            unidad_medida_id=2,  # cápsula
            proveedor_id=3,  # Farmacéutica DEF
            precio_compra=0.80,
            precio_venta=2.00,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Omeprazol 20mg",
            codigo="MED-004",
            referencia="REF-OME-20",
            descripcion="Inhibidor de la bomba de protones",
            categoria_id=1,  # Medicamentos
            unidad_medida_id=2,  # cápsula
            proveedor_id=4,  # Farmacéutica GHI
            precio_compra=0.70,
            precio_venta=1.80,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Losartán 50mg",
            codigo="MED-005",
            referencia="REF-LOS-50",
            descripcion="Antihipertensivo",
            categoria_id=3,  # Cardiovascular
            unidad_medida_id=1,  # tableta
            proveedor_id=5,  # Farmacéutica JKL
            precio_compra=0.90,
            precio_venta=2.20,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Metformina 850mg",
            codigo="MED-006",
            referencia="REF-MET-850",
            descripcion="Antidiabético oral",
            categoria_id=4,  # Endocrinología
            unidad_medida_id=1,  # tableta
            proveedor_id=6,  # Farmacéutica MNO
            precio_compra=0.40,
            precio_venta=1.00,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Simvastatina 20mg",
            codigo="MED-007",
            referencia="REF-SIM-20",
            descripcion="Hipolipemiante",
            categoria_id=3,  # Cardiovascular
            unidad_medida_id=1,  # tableta
            proveedor_id=7,  # Farmacéutica PQR
            precio_compra=0.75,
            precio_venta=1.90,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Enalapril 10mg",
            codigo="MED-008",
            referencia="REF-ENA-10",
            descripcion="Antihipertensivo IECA",
            categoria_id=3,  # Cardiovascular
            unidad_medida_id=1,  # tableta
            proveedor_id=8,  # Farmacéutica STU
            precio_compra=0.55,
            precio_venta=1.40,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Aspirina 100mg",
            codigo="MED-009",
            referencia="REF-ASP-100",
            descripcion="Antiagregante plaquetario",
            categoria_id=3,  # Cardiovascular
            unidad_medida_id=1,  # tableta
            proveedor_id=9,  # Farmacéutica VWX
            precio_compra=0.30,
            precio_venta=0.80,
            status="active",
            is_deleted=False
        ),
        Product(
            nombre="Cetirizina 10mg",
            codigo="MED-010",
            referencia="REF-CET-10",
            descripcion="Antihistamínico",
            categoria_id=5,  # Alergias
            unidad_medida_id=1,  # tableta
            proveedor_id=10,  # Farmacéutica YZA
            precio_compra=0.45,
            precio_venta=1.10,
            status="active",
            is_deleted=False
        ),
    ]
    
    db.session.bulk_save_objects(products)
    db.session.commit()
    
    print(f"✅ Creados {len(products)} productos")


def create_sample_inventory_items():
    """
    Crea items de inventario de muestra
    
    Los product_id (1-10) corresponden a productos en la tabla products.
    Aquí solo se almacena: stock y ubicación en bodega.
    """
    print("📋 Creando items de inventario de muestra...")
    
    items = [
        # Items con ubicación en bodega
        InventoryItem(
            product_id=1,  # Paracetamol 500mg
            pasillo="A",
            estanteria="01",
            nivel="1",
            cantidad=500,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=2,  # Ibuprofeno 400mg
            pasillo="A",
            estanteria="02",
            nivel="1",
            cantidad=300,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=3,  # Amoxicilina 500mg
            pasillo="A",
            estanteria="03",
            nivel="2",
            cantidad=200,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=4,  # Omeprazol 20mg
            pasillo="B",
            estanteria="01",
            nivel="1",
            cantidad=400,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=5,  # Losartán 50mg
            pasillo="B",
            estanteria="02",
            nivel="1",
            cantidad=250,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=6,  # Metformina 850mg
            pasillo="B",
            estanteria="03",
            nivel="2",
            cantidad=350,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=7,  # Simvastatina 20mg
            pasillo="C",
            estanteria="01",
            nivel="1",
            cantidad=180,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=8,  # Enalapril 10mg
            pasillo="C",
            estanteria="02",
            nivel="2",
            cantidad=220,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=9,  # Aspirina 100mg
            pasillo="C",
            estanteria="03",
            nivel="1",
            cantidad=600,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=10,  # Cetirizina 10mg
            pasillo="D",
            estanteria="01",
            nivel="1",
            cantidad=150,
            status=InventoryStatus.AVAILABLE.value
        ),
        # Item adicional del mismo producto en otra ubicación
        InventoryItem(
            product_id=1,  # Paracetamol 500mg (otra ubicación)
            pasillo="D",
            estanteria="02",
            nivel="2",
            cantidad=100,
            status=InventoryStatus.AVAILABLE.value
        ),
    ]
    
    db.session.bulk_save_objects(items)
    db.session.commit()
    
    print(f"✅ Creados {len(items)} items de inventario")


def create_sample_movements():
    """Crea movimientos de inventario de muestra para trazabilidad"""
    print("📊 Creando movimientos de inventario de muestra...")
    
    # Obtener algunos items para crear movimientos
    item1 = InventoryItem.query.filter_by(product_id=1).first()
    item2 = InventoryItem.query.filter_by(product_id=2).first()
    
    if not item1 or not item2:
        print("⚠️  No se encontraron items para crear movimientos")
        return
    
    movements = [
        # Entrada inicial
        InventoryMovement(
            inventory_item_id=item1.id,
            product_id=item1.product_id,
            tipo=MovementType.ENTRADA.value,
            cantidad=500,
            cantidad_anterior=0,
            cantidad_nueva=500,
            motivo="Recepción de compra inicial",
            documento_referencia="OC-2024-001",
            usuario_id=1,
            usuario_nombre="Admin Sistema",
            fecha_movimiento=datetime.utcnow() - timedelta(days=30)
        ),
        # Salida por venta
        InventoryMovement(
            inventory_item_id=item1.id,
            product_id=item1.product_id,
            tipo=MovementType.SALIDA.value,
            cantidad=50,
            cantidad_anterior=500,
            cantidad_nueva=450,
            motivo="Venta a cliente",
            documento_referencia="INV-2024-0123",
            usuario_id=2,
            usuario_nombre="Operador Ventas",
            fecha_movimiento=datetime.utcnow() - timedelta(days=15)
        ),
        # Entrada para item2
        InventoryMovement(
            inventory_item_id=item2.id,
            product_id=item2.product_id,
            tipo=MovementType.ENTRADA.value,
            cantidad=300,
            cantidad_anterior=0,
            cantidad_nueva=300,
            motivo="Recepción de compra",
            documento_referencia="OC-2024-002",
            usuario_id=1,
            usuario_nombre="Admin Sistema",
            fecha_movimiento=datetime.utcnow() - timedelta(days=25)
        ),
        # Ajuste de inventario
        InventoryMovement(
            inventory_item_id=item2.id,
            product_id=item2.product_id,
            tipo=MovementType.AJUSTE.value,
            cantidad=20,
            cantidad_anterior=300,
            cantidad_nueva=280,
            motivo="Ajuste por conteo físico",
            documento_referencia="AJ-2024-001",
            usuario_id=1,
            usuario_nombre="Admin Sistema",
            fecha_movimiento=datetime.utcnow() - timedelta(days=10)
        ),
    ]
    
    db.session.bulk_save_objects(movements)
    db.session.commit()
    
    print(f"✅ Creados {len(movements)} movimientos de inventario")


def init_db():
    """Función principal de inicialización"""
    print("\n" + "="*60)
    print("🚀 INICIALIZACIÓN DE BASE DE DATOS - INVENTORY SERVICE")
    print("="*60 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            drop_all_tables()
            create_all_tables()
            create_sample_products()
            create_sample_inventory_items()
            create_sample_movements()
            
            # Estadísticas
            total_products = Product.query.count()
            total_items = InventoryItem.query.count()
            total_movements = InventoryMovement.query.count()
            
            print("\n" + "="*60)
            print("✅ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
            print("="*60)
            print("\n📊 Estadísticas:")
            print(f"   - Productos creados: {total_products}")
            print(f"   - Items de inventario: {total_items}")
            print(f"   - Movimientos registrados: {total_movements}")
            print("\n💡 Nota: Los productos se crearon para testing.")
            print("   En producción, products-service los crea.")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error durante la inicialización: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    init_db()
