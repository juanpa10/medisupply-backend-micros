"""
Script de prueba para verificar el manejo de rutas en Windows
"""
import os
from pathlib import Path

# Simular diferentes formatos de rutas que pueden venir de la BD
test_paths = [
    # Ruta con barras simples (puede venir de BD)
    r"C:\Users\stiwa\Documents\VSCode Projects\Projects\Karen\medisupply-backend-micros\crm-service\uploads\certificates\test.pdf",
    # Ruta con barras dobles (escapadas)
    "C:\\Users\\stiwa\\Documents\\VSCode Projects\\Projects\\Karen\\medisupply-backend-micros\\crm-service\\uploads\\certificates\\test.pdf",
    # Ruta relativa
    "./uploads/certificates/test.pdf",
    # Ruta relativa sin ./
    "uploads/certificates/test.pdf",
]

print("=" * 80)
print("PRUEBA DE MANEJO DE RUTAS EN WINDOWS")
print("=" * 80)

for i, test_path in enumerate(test_paths, 1):
    print(f"\n{i}. Ruta de entrada:")
    print(f"   {repr(test_path)}")
    
    # Convertir a Path
    path = Path(test_path)
    
    print(f"   Es absoluta: {path.is_absolute()}")
    
    # Si es relativa, convertir a absoluta
    if not path.is_absolute():
        current_file = Path(__file__).resolve()
        app_root = current_file.parent
        path = app_root / path
        print(f"   Convertida a absoluta desde: {app_root}")
    
    # Resolver la ruta
    resolved = path.resolve()
    
    print(f"   Ruta resuelta: {resolved}")
    print(f"   Como string: {str(resolved)}")
    print(f"   Existe: {resolved.exists()}")
    print(f"   Repr: {repr(str(resolved))}")

print("\n" + "=" * 80)
print("VERIFICACIÓN DE DIRECTORIOS")
print("=" * 80)

# Verificar el directorio de uploads
current_file = Path(__file__).resolve()
app_root = current_file.parent
uploads_dir = app_root / "uploads" / "certificates"

print(f"\nDirectorio raíz de la app: {app_root}")
print(f"Directorio de certificados: {uploads_dir}")
print(f"Existe: {uploads_dir.exists()}")

if uploads_dir.exists():
    print(f"\nArchivos en {uploads_dir}:")
    for file in uploads_dir.iterdir():
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
else:
    print(f"\n⚠️ El directorio no existe: {uploads_dir}")

print("\n" + "=" * 80)
