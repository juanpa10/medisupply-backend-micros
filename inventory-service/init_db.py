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
from sqlalchemy import text
from app.modules.inventory.models import InventoryItem, InventoryMovement
from app.shared.enums import InventoryStatus, MovementType

# Note: Product model not imported as we use raw SQL for products table


def drop_all_tables():
    """Elimina todas las tablas de la base de datos"""
    print("🗑️  Eliminando tablas existentes (solo tablas manejadas por el seeder)...")
    # Avoid calling db.drop_all() because SQLAlchemy metadata includes FK
    # relationships to tables that may not exist in some deployments (eg
    # 'proveedores'). Use raw DROP TABLE IF EXISTS for the specific tables
    # we manage here so we don't trigger NoReferencedTableError.
    # Only drop inventory-specific tables. Keep `products` table to avoid
    # removing real product data in environments where products-service
    # is authoritative. This makes the seeder safer / idempotent.
    sql = '''
    DROP TABLE IF EXISTS inventory_movements CASCADE;
    DROP TABLE IF EXISTS inventory_items CASCADE;
    '''
    db.session.execute(text(sql))
    db.session.commit()
    print("✅ Tablas (específicas) eliminadas")


def create_all_tables():
    """Crea todas las tablas definidas en los modelos"""
    print("📦 Creando tablas necesarias (inventory_items, inventory_movements)...")
    # Create the inventory tables using raw SQL so we don't rely on ORM
    # metadata that includes external FK tables.
    create_inventory_items = '''
    CREATE TABLE IF NOT EXISTS inventory_items (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
        created_by VARCHAR(100),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        updated_by VARCHAR(100),
        deleted_at TIMESTAMP WITHOUT TIME ZONE,
        deleted_by VARCHAR(100),
        is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
        product_id INTEGER NOT NULL,
        pasillo VARCHAR(20),
        estanteria VARCHAR(20),
        nivel VARCHAR(20),
        cantidad NUMERIC(10,2) NOT NULL DEFAULT 0,
        status VARCHAR(20) NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_location ON inventory_items (pasillo, estanteria, nivel);
    CREATE INDEX IF NOT EXISTS idx_product_id ON inventory_items (product_id);
    '''

    create_inventory_movements = '''
    CREATE TABLE IF NOT EXISTS inventory_movements (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
        created_by VARCHAR(100),
        updated_at TIMESTAMP WITHOUT TIME ZONE,
        updated_by VARCHAR(100),
        deleted_at TIMESTAMP WITHOUT TIME ZONE,
        deleted_by VARCHAR(100),
        is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
        inventory_item_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        tipo VARCHAR(30) NOT NULL,
        cantidad NUMERIC(10,2) NOT NULL,
        cantidad_anterior NUMERIC(10,2),
        cantidad_nueva NUMERIC(10,2),
        motivo VARCHAR(200),
        documento_referencia VARCHAR(100),
        usuario_id INTEGER,
        usuario_nombre VARCHAR(200),
        fecha_movimiento TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS idx_product_movement ON inventory_movements (product_id, fecha_movimiento);
    CREATE INDEX IF NOT EXISTS idx_item_movement ON inventory_movements (inventory_item_id, fecha_movimiento);
    CREATE INDEX IF NOT EXISTS idx_tipo_fecha ON inventory_movements (tipo, fecha_movimiento);
    '''

    db.session.execute(text(create_inventory_items))
    db.session.execute(text(create_inventory_movements))
    db.session.commit()
    print("✅ Tablas de inventario creadas (si no existían)")


def create_sample_products():
    """
    Crea productos de muestra en la tabla products
    
    NOTA: Normalmente estos productos se crean desde products-service.
    Aquí los creamos solo para propósitos de testing y demostración.
    Los campos categoria_id, unidad_medida_id y proveedor_id son Foreign Keys.
    """
    print("🏷️  Creando productos de muestra (tabla simple sin FKs)...")

    # Some deployments do not include the referenced FK tables (categorias,
    # unidades_medida, proveedores). To keep init_db safe for local dev we
    # create a simple products table (if it doesn't exist) with the common
    # searchable columns (both English and Spanish names) and insert sample
    # rows via raw SQL. This avoids ORM FK constraints issues.
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(200),
        nombre VARCHAR(200),
        code VARCHAR(50),
        codigo VARCHAR(50),
        reference VARCHAR(100),
        referencia VARCHAR(100),
        description TEXT,
        descripcion TEXT,
        unit_price NUMERIC(10,2),
        precio_venta NUMERIC(10,2),
        status VARCHAR(20),
        is_deleted BOOLEAN DEFAULT FALSE
    );
    '''
    db.session.execute(text(create_table_sql))
    db.session.commit()

    sample_products = [
        {
            'name': 'Paracetamol 500mg', 'nombre': 'Paracetamol 500mg',
            'code': 'MED-001', 'codigo': 'MED-001', 'reference': 'REF-PARA-500', 'referencia': 'REF-PARA-500',
            'description': 'Analgésico y antipirético', 'descripcion': 'Analgésico y antipirético',
            'unit_price': 1.20, 'precio_venta': 1.20, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Ibuprofeno 400mg', 'nombre': 'Ibuprofeno 400mg',
            'code': 'MED-002', 'codigo': 'MED-002', 'reference': 'REF-IBU-400', 'referencia': 'REF-IBU-400',
            'description': 'Antiinflamatorio no esteroideo', 'descripcion': 'Antiinflamatorio no esteroideo',
            'unit_price': 1.50, 'precio_venta': 1.50, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Amoxicilina 500mg', 'nombre': 'Amoxicilina 500mg',
            'code': 'MED-003', 'codigo': 'MED-003', 'reference': 'REF-AMO-500', 'referencia': 'REF-AMO-500',
            'description': 'Antibiótico de amplio espectro', 'descripcion': 'Antibiótico de amplio espectro',
            'unit_price': 2.00, 'precio_venta': 2.00, 'status': 'active', 'is_deleted': False
        }
    ,
        {
            'name': 'Omeprazol 20mg', 'nombre': 'Omeprazol 20mg',
            'code': 'MED-004', 'codigo': 'MED-004', 'reference': 'REF-OME-20', 'referencia': 'REF-OME-20',
            'description': 'Inhibidor de la bomba de protones', 'descripcion': 'Inhibidor de la bomba de protones',
            'unit_price': 1.80, 'precio_venta': 1.80, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Losartán 50mg', 'nombre': 'Losartán 50mg',
            'code': 'MED-005', 'codigo': 'MED-005', 'reference': 'REF-LOS-50', 'referencia': 'REF-LOS-50',
            'description': 'Antihipertensivo', 'descripcion': 'Antihipertensivo',
            'unit_price': 2.20, 'precio_venta': 2.20, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Metformina 850mg', 'nombre': 'Metformina 850mg',
            'code': 'MED-006', 'codigo': 'MED-006', 'reference': 'REF-MET-850', 'referencia': 'REF-MET-850',
            'description': 'Antidiabético oral', 'descripcion': 'Antidiabético oral',
            'unit_price': 1.00, 'precio_venta': 1.00, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Simvastatina 20mg', 'nombre': 'Simvastatina 20mg',
            'code': 'MED-007', 'codigo': 'MED-007', 'reference': 'REF-SIM-20', 'referencia': 'REF-SIM-20',
            'description': 'Hipolipemiante', 'descripcion': 'Hipolipemiante',
            'unit_price': 1.90, 'precio_venta': 1.90, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Aspirina 100mg', 'nombre': 'Aspirina 100mg',
            'code': 'MED-008', 'codigo': 'MED-008', 'reference': 'REF-ASP-100', 'referencia': 'REF-ASP-100',
            'description': 'Antiagregante plaquetario', 'descripcion': 'Antiagregante plaquetario',
            'unit_price': 0.80, 'precio_venta': 0.80, 'status': 'active', 'is_deleted': False
        },
        {
            'name': 'Cetirizina 10mg', 'nombre': 'Cetirizina 10mg',
            'code': 'MED-009', 'codigo': 'MED-009', 'reference': 'REF-CET-10', 'referencia': 'REF-CET-10',
            'description': 'Antihistamínico', 'descripcion': 'Antihistamínico',
            'unit_price': 1.10, 'precio_venta': 1.10, 'status': 'active', 'is_deleted': False
        }
    ]

    # Discover which columns actually exist in the current `products` table
    col_q = "SELECT column_name FROM information_schema.columns WHERE table_name = 'products'"
    cols = [row[0] for row in db.session.execute(text(col_q)).fetchall()]

    # Build a safe INSERT statement using only the columns that exist
    desired_cols = ['name', 'nombre', 'code', 'codigo', 'reference', 'referencia',
                    'description', 'descripcion', 'unit_price', 'precio_venta', 'status', 'is_deleted']
    insert_cols = [c for c in desired_cols if c in cols]

    if insert_cols:
        insert_sql = f"INSERT INTO products ({', '.join(insert_cols)}) VALUES ({', '.join(':' + c for c in insert_cols)}) RETURNING id;"
    else:
        # No writable columns found; skip insertion
        print('⚠️  No matching product columns found, skipping product inserts')
        insert_sql = None

    created = 0
    for p in sample_products:
        # Build an existence check using only available identifier columns
        idents = []
        if 'codigo' in cols:
            idents.append('codigo = :codigo')
        if 'code' in cols:
            idents.append('code = :code')

        cnt = 0
        if idents:
            exists_sql = 'SELECT count(1) AS cnt FROM products WHERE ' + ' OR '.join(idents)
            try:
                res = db.session.execute(text(exists_sql), {'codigo': p.get('codigo'), 'code': p.get('code')})
                cnt = int(res.scalar() or 0)
            except Exception:
                # If the existence check fails for any reason, fallback to 0 so insert will be attempted
                cnt = 0
        else:
            # No identifier columns available, assume product doesn't exist and attempt insert
            cnt = 0

        if cnt == 0 and insert_sql:
            # Prepare parameters only for columns that we will insert
            params = {k: v for k, v in p.items() if k in insert_cols}
            try:
                db.session.execute(text(insert_sql), params)
                created += 1
            except Exception:
                import traceback
                print('⚠️  Failed to insert sample product:')
                traceback.print_exc()

    db.session.commit()

    print(f"✅ Creados {created} productos (tabla simple)")


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
            product_id=8,  # Aspirina 100mg
            pasillo="C",
            estanteria="02",
            nivel="2",
            cantidad=220,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=9,  # Cetirizina 10mg
            pasillo="C",
            estanteria="03",
            nivel="1",
            cantidad=600,
            status=InventoryStatus.AVAILABLE.value
        ),
        InventoryItem(
            product_id=9,  # Cetirizina 10mg
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
            
            # Estadísticas: usar SQL directo para evitar columnas faltantes en la
            # tabla `products` cuando el ORM Product tiene FKs/columnas que no
            # existen en esta tabla simple creada por el seeder.
            total_products = int(db.session.execute(text('SELECT count(*) FROM products')).scalar() or 0)
            total_items = int(db.session.execute(text('SELECT count(*) FROM inventory_items')).scalar() or 0)
            total_movements = int(db.session.execute(text('SELECT count(*) FROM inventory_movements')).scalar() or 0)
            
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
