#!/usr/bin/env python3
"""
Simple test to verify database connection and Flask app creation
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Configurar la URL de la base de datos ANTES de importar la app
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://app:app@localhost:5432/medisupplydb'

from app import create_app
from app.config.database import db

def test_connection():
    """Test de conexión básica"""
    print("🧪 Probando conexión a la base de datos...")
    print(f"🔗 DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    try:
        # Crear la app Flask
        app = create_app('development')
        print("✅ App Flask creada correctamente")
        
        with app.app_context():
            # Probar la conexión
            print("🔧 Probando conexión a la base de datos...")
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✅ Conexión exitosa a la base de datos")
                
                # Intentar crear tablas
                print("🔧 Creando tablas...")
                db.create_all()
                print("✅ Tablas creadas/verificadas exitosamente")
                return True
            else:
                print("❌ Conexión falló")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 ¡Test de conexión exitoso!")
    else:
        print("\n💥 Test de conexión falló")
        sys.exit(1)