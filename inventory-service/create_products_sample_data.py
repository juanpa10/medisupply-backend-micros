"""
Script para crear datos de muestra para el módulo de productos

Incluye:
- Categorías base
- Unidades de medida 
- Proveedores de ejemplo
- Productos de muestra con documentación requerida
"""
import sys
import os
from pathlib import Path

# IMPORTANTE: Configurar la URL de la base de datos ANTES de cualquier import de la app
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://app:app@localhost:5432/medisupplydb'

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app import create_app
from app.config.database import db
from app.modules.products.models import Product, ProductFile, Categoria, UnidadMedida, Proveedor
from app.modules.products.service import ProductService, CategoriaService, UnidadMedidaService, ProveedorService


def create_sample_master_data():
    """Crea datos maestros básicos"""
    print("📁 Creando datos maestros...")
    
    categoria_service = CategoriaService()
    unidad_service = UnidadMedidaService()
    proveedor_service = ProveedorService()
    
    # Categorías
    categorias = [
        {'nombre': 'Medicamentos', 'descripcion': 'Medicamentos de uso general'},
        {'nombre': 'Antibióticos', 'descripcion': 'Antibióticos y antimicrobianos'},
        {'nombre': 'Cardiovascular', 'descripcion': 'Medicamentos para el sistema cardiovascular'},
        {'nombre': 'Endocrinología', 'descripcion': 'Medicamentos endocrinos y metabólicos'},
        {'nombre': 'Alergias', 'descripcion': 'Medicamentos para alergias y asma'},
        {'nombre': 'Material Médico', 'descripcion': 'Equipos y material médico'},
        {'nombre': 'Suministros', 'descripcion': 'Suministros médicos diversos'}
    ]
    
    created_categorias = []
    for cat_data in categorias:
        try:
            categoria = categoria_service.create_categoria(cat_data, 'system')
            created_categorias.append(categoria)
            print(f"  ✅ Categoría creada: {categoria.nombre}")
        except Exception as e:
            print(f"  ⚠️ Error en categoría {cat_data['nombre']}: {e}")
    
    # Unidades de medida
    unidades = [
        {'nombre': 'Tableta', 'abreviatura': 'TAB', 'descripcion': 'Tableta o comprimido'},
        {'nombre': 'Cápsula', 'abreviatura': 'CAP', 'descripcion': 'Cápsula'},
        {'nombre': 'Mililitro', 'abreviatura': 'ML', 'descripcion': 'Mililitro de líquido'},
        {'nombre': 'Gramo', 'abreviatura': 'GR', 'descripcion': 'Gramo de peso'},
        {'nombre': 'Unidad', 'abreviatura': 'UND', 'descripcion': 'Unidad individual'},
        {'nombre': 'Frasco', 'abreviatura': 'FRS', 'descripcion': 'Frasco de medicamento'},
        {'nombre': 'Ampolla', 'abreviatura': 'AMP', 'descripcion': 'Ampolla inyectable'},
        {'nombre': 'Sobre', 'abreviatura': 'SOB', 'descripcion': 'Sobre o sachét'}
    ]
    
    created_unidades = []
    for unidad_data in unidades:
        try:
            unidad = unidad_service.create_unidad_medida(unidad_data, 'system')
            created_unidades.append(unidad)
            print(f"  ✅ Unidad creada: {unidad.nombre} ({unidad.abreviatura})")
        except Exception as e:
            print(f"  ⚠️ Error en unidad {unidad_data['nombre']}: {e}")
    
    # Proveedores
    proveedores = [
        {
            'nombre': 'Farmacéutica Nacional SA',
            'nit': '900123456-7',
            'contacto_nombre': 'Carlos Rodríguez',
            'contacto_telefono': '3001234567',
            'contacto_email': 'carlos@farmacol.com',
            'direccion': 'Calle 123 #45-67, Bogotá',
            'pais': 'Colombia'
        },
        {
            'nombre': 'MediSupply International',
            'nit': '900234567-8',
            'contacto_nombre': 'Ana García',
            'contacto_telefono': '3007654321',
            'contacto_email': 'ana@medisupply.com',
            'direccion': 'Carrera 78 #90-12, Medellín',
            'pais': 'Colombia'
        },
        {
            'nombre': 'Laboratorios Unidos',
            'nit': '900345678-9',
            'contacto_nombre': 'Luis Martínez',
            'contacto_telefono': '3009876543',
            'contacto_email': 'luis@labunidos.com',
            'direccion': 'Avenida 12 #34-56, Cali',
            'pais': 'Colombia'
        },
        {
            'nombre': 'Global Pharma Corp',
            'contacto_nombre': 'Sarah Johnson',
            'contacto_telefono': '+1-555-123-4567',
            'contacto_email': 'sarah@globalpharma.com',
            'direccion': '123 Medical Drive, Miami, FL',
            'pais': 'Estados Unidos'
        },
        {
            'nombre': 'European Medical Supplies',
            'contacto_nombre': 'Hans Mueller',
            'contacto_telefono': '+49-30-12345678',
            'contacto_email': 'hans@euromedical.de',
            'direccion': 'Friedrichstr. 123, Berlin',
            'pais': 'Alemania'
        }
    ]
    
    created_proveedores = []
    for prov_data in proveedores:
        try:
            proveedor = proveedor_service.create_proveedor(prov_data, 'system')
            created_proveedores.append(proveedor)
            print(f"  ✅ Proveedor creado: {proveedor.nombre}")
        except Exception as e:
            print(f"  ⚠️ Error en proveedor {prov_data['nombre']}: {e}")
    
    return created_categorias, created_unidades, created_proveedores


def create_sample_products():
    """Crea productos de muestra"""
    print("🏷️ Creando productos de muestra...")
    
    product_service = ProductService()
    
    # Obtener IDs de datos maestros
    categorias = db.session.query(Categoria).filter(Categoria.is_deleted == False).all()
    unidades = db.session.query(UnidadMedida).filter(UnidadMedida.is_deleted == False).all()
    proveedores = db.session.query(Proveedor).filter(Proveedor.is_deleted == False).all()
    
    if not categorias or not unidades or not proveedores:
        print("  ❌ Faltan datos maestros. Ejecute create_sample_master_data() primero.")
        return []
    
    # Productos de ejemplo
    productos = [
        {
            'nombre': 'Paracetamol 500mg',
            'codigo': 'PARA-500',
            'referencia': 'REF-PARA-500',
            'descripcion': 'Analgésico y antipirético para el alivio del dolor y la fiebre. Indicado para dolor leve a moderado.',
            'categoria_id': categorias[0].id,  # Medicamentos
            'unidad_medida_id': unidades[0].id,  # Tableta
            'proveedor_id': proveedores[0].id,
            'precio_compra': 0.50,
            'precio_venta': 0.80,
            'requiere_ficha_tecnica': True,
            'requiere_condiciones_almacenamiento': True,
            'requiere_certificaciones_sanitarias': True
        },
        {
            'nombre': 'Amoxicilina 250mg',
            'codigo': 'AMOX-250',
            'referencia': 'REF-AMOX-250',
            'descripcion': 'Antibiótico de amplio espectro del grupo de las penicilinas. Para infecciones bacterianas.',
            'categoria_id': categorias[1].id if len(categorias) > 1 else categorias[0].id,  # Antibióticos
            'unidad_medida_id': unidades[1].id if len(unidades) > 1 else unidades[0].id,  # Cápsula
            'proveedor_id': proveedores[1].id if len(proveedores) > 1 else proveedores[0].id,
            'precio_compra': 1.20,
            'precio_venta': 1.80,
            'requiere_ficha_tecnica': True,
            'requiere_condiciones_almacenamiento': True,
            'requiere_certificaciones_sanitarias': True
        },
        {
            'nombre': 'Atorvastatina 20mg',
            'codigo': 'ATOR-20',
            'referencia': 'REF-ATOR-20',
            'descripcion': 'Medicamento para reducir el colesterol y prevenir enfermedades cardiovasculares.',
            'categoria_id': categorias[2].id if len(categorias) > 2 else categorias[0].id,  # Cardiovascular
            'unidad_medida_id': unidades[0].id,  # Tableta
            'proveedor_id': proveedores[2].id if len(proveedores) > 2 else proveedores[0].id,
            'precio_compra': 2.50,
            'precio_venta': 4.00,
            'requiere_ficha_tecnica': True,
            'requiere_condiciones_almacenamiento': True,
            'requiere_certificaciones_sanitarias': True
        },
        {
            'nombre': 'Metformina 850mg',
            'codigo': 'METF-850',
            'referencia': 'REF-METF-850',
            'descripcion': 'Antidiabético oral para el tratamiento de diabetes tipo 2. Reduce la glucosa en sangre.',
            'categoria_id': categorias[3].id if len(categorias) > 3 else categorias[0].id,  # Endocrinología
            'unidad_medida_id': unidades[0].id,  # Tableta
            'proveedor_id': proveedores[3].id if len(proveedores) > 3 else proveedores[0].id,
            'precio_compra': 1.00,
            'precio_venta': 1.50,
            'requiere_ficha_tecnica': True,
            'requiere_condiciones_almacenamiento': False,
            'requiere_certificaciones_sanitarias': True
        },
        {
            'nombre': 'Cetirizina 10mg',
            'codigo': 'CETI-10',
            'referencia': 'REF-CETI-10',
            'descripcion': 'Antihistamínico para el tratamiento de alergias, rinitis y urticaria.',
            'categoria_id': categorias[4].id if len(categorias) > 4 else categorias[0].id,  # Alergias
            'unidad_medida_id': unidades[0].id,  # Tableta
            'proveedor_id': proveedores[4].id if len(proveedores) > 4 else proveedores[0].id,
            'precio_compra': 0.80,
            'precio_venta': 1.20,
            'requiere_ficha_tecnica': True,
            'requiere_condiciones_almacenamiento': True,
            'requiere_certificaciones_sanitarias': False
        },
        {
            'nombre': 'Termómetro Digital',
            'codigo': 'TERM-DIG',
            'referencia': 'REF-TERM-001',
            'descripcion': 'Termómetro digital de precisión para medición de temperatura corporal.',
            'categoria_id': categorias[5].id if len(categorias) > 5 else categorias[0].id,  # Material Médico
            'unidad_medida_id': unidades[4].id if len(unidades) > 4 else unidades[0].id,  # Unidad
            'proveedor_id': proveedores[0].id,
            'precio_compra': 15.00,
            'precio_venta': 25.00,
            'requiere_ficha_tecnica': False,
            'requiere_condiciones_almacenamiento': False,
            'requiere_certificaciones_sanitarias': True
        }
    ]
    
    created_products = []
    for prod_data in productos:
        try:
            product = product_service.create_product(prod_data, current_user='system')
            created_products.append(product)
            print(f"  ✅ Producto creado: {product.codigo} - {product.nombre}")
            
            # Mostrar estado del catálogo
            catalog_status = product_service.get_product_catalog_status(product.id)
            print(f"    📊 Estado: {catalog_status['catalog_status']} - {catalog_status['message']}")
            
        except Exception as e:
            print(f"  ❌ Error en producto {prod_data['codigo']}: {e}")
            import traceback
            traceback.print_exc()
    
    return created_products


def create_sample_files():
    """Crea archivos de ejemplo para productos"""
    print("📎 Creando archivos de ejemplo...")
    
    # Para simplicidad, creamos archivos de texto de ejemplo
    upload_dir = Path('uploads/products')
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    sample_files = {
        'technical_sheet': 'Ficha técnica del producto\nComposición: ...\nIndicaciones: ...\nDosis: ...',
        'storage_conditions': 'Condiciones de almacenamiento\nTemperatura: 15-25°C\nHumedad: <60%\nLuz: Proteger de la luz',
        'health_certifications': 'Certificaciones sanitarias\nINVIMA: Aprobado\nFDA: Pendiente\nEMA: Aprobado'
    }
    
    # Crear archivos de ejemplo para el primer producto
    products = db.session.query(Product).filter(Product.is_deleted == False).first()
    if not products:
        print("  ⚠️ No hay productos creados")
        return
    
    from app.modules.products.service import ProductService
    product_service = ProductService()
    
    for file_category, content in sample_files.items():
        try:
            # Crear archivo temporal
            filename = f"ejemplo_{file_category}.txt"
            file_path = upload_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Archivo de ejemplo creado: {filename}")
            
            # Nota: En una implementación real, usarías FileStorage para subir archivos
            # Aquí solo creamos los archivos como ejemplo de estructura
            
        except Exception as e:
            print(f"  ❌ Error creando archivo {file_category}: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando creación de datos de muestra para productos...")
    print(f"🔧 Database URL configurada: {os.environ.get('DATABASE_URL')}")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Crear tablas si no existen
            db.create_all()
            print("✅ Tablas verificadas/creadas")
            
            # Crear datos maestros
            categorias, unidades, proveedores = create_sample_master_data()
            print(f"✅ Creados: {len(categorias)} categorías, {len(unidades)} unidades, {len(proveedores)} proveedores")
            
            # Crear productos
            products = create_sample_products()
            print(f"✅ Creados: {len(products)} productos")
            
            # Crear archivos de ejemplo
            create_sample_files()
            
            print("\n🎉 ¡Datos de muestra creados exitosamente!")
            print("\n📋 Resumen:")
            print(f"   - Categorías: {len(categorias)}")
            print(f"   - Unidades de medida: {len(unidades)}")
            print(f"   - Proveedores: {len(proveedores)}")
            print(f"   - Productos: {len(products)}")
            
            print("\n🔗 Endpoints disponibles:")
            print("   - GET /api/v1/products - Listar productos")
            print("   - GET /api/v1/products/search?q=paracetamol - Buscar productos")
            print("   - POST /api/v1/products - Crear producto")
            print("   - GET /api/v1/categorias - Listar categorías")
            print("   - GET /api/v1/unidades-medida - Listar unidades")
            print("   - GET /api/v1/proveedores - Listar proveedores")
            print("   - GET /api/v1/products/docs - Documentación completa")
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)