"""
Script para verificar las rutas guardadas en la base de datos
"""
from app import create_app
from app.modules.suppliers.models import Supplier
from pathlib import Path

app = create_app()

with app.app_context():
    print("=" * 80)
    print("RUTAS DE CERTIFICADOS EN LA BASE DE DATOS")
    print("=" * 80)
    
    suppliers = Supplier.query.filter_by(is_deleted=False).all()
    
    if not suppliers:
        print("\n⚠️ No hay proveedores en la base de datos")
    else:
        for supplier in suppliers:
            print(f"\n{'=' * 80}")
            print(f"Proveedor: {supplier.razon_social} (ID: {supplier.id})")
            print(f"NIT: {supplier.nit}")
            print(f"\nRuta almacenada en BD:")
            print(f"  {repr(supplier.certificado_path)}")
            
            # Analizar la ruta
            path = Path(supplier.certificado_path)
            print(f"\n¿Es absoluta?: {path.is_absolute()}")
            
            # Si es relativa, calcular la absoluta
            if not path.is_absolute():
                current_file = Path(__file__).resolve()
                app_root = current_file.parent
                absolute_path = app_root / path
                print(f"Ruta relativa convertida a absoluta:")
                print(f"  {absolute_path}")
                resolved_path = absolute_path.resolve()
            else:
                resolved_path = path.resolve()
            
            print(f"\nRuta resuelta:")
            print(f"  {resolved_path}")
            print(f"  Repr: {repr(str(resolved_path))}")
            
            # Verificar si existe
            exists = resolved_path.exists()
            print(f"\n¿Archivo existe?: {exists}")
            
            if exists:
                size = resolved_path.stat().st_size
                print(f"Tamaño: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
            else:
                print(f"❌ ARCHIVO NO ENCONTRADO")
                
                # Buscar el archivo en el directorio de certificados
                certs_dir = Path(__file__).parent / "uploads" / "certificates"
                filename = path.name
                possible_path = certs_dir / filename
                
                print(f"\nBuscando en directorio de certificados:")
                print(f"  {possible_path}")
                print(f"  ¿Existe?: {possible_path.exists()}")
    
    print(f"\n{'=' * 80}")
