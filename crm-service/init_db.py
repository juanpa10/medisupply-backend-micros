"""
Script para inicializar la base de datos con datos de prueba
"""
import os
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.config.database import db
from app.modules.suppliers.models import Supplier


def init_db():
    """Inicializa la base de datos"""
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas exitosamente")


def seed_data():
    """Carga datos de prueba"""
    app = create_app()
    
    with app.app_context():
        # Verificar si ya hay datos
        if Supplier.query.count() > 0:
            print("⚠️  Ya existen datos en la base de datos")
            return
        
        # Crear proveedores de prueba
        suppliers = [
            Supplier(
                razon_social="Farmacéutica Colombia S.A.",
                nit="900123456-7",
                representante_legal="Carlos Rodríguez",
                pais="Colombia",
                nombre_contacto="Ana López",
                celular_contacto="3001234567",
                certificado_filename="cert_farmacol.pdf",
                certificado_path="/tmp/cert_farmacol.pdf",
                email="contacto@farmacol.com",
                ciudad="Bogotá",
                created_by="admin"
            ),
            Supplier(
                razon_social="Laboratorios Unidos México",
                nit="LUM-987654321",
                representante_legal="María González",
                pais="México",
                nombre_contacto="Juan Pérez",
                celular_contacto="+525512345678",
                certificado_filename="cert_labmex.pdf",
                certificado_path="/tmp/cert_labmex.pdf",
                email="info@labmex.mx",
                ciudad="Ciudad de México",
                created_by="admin"
            ),
            Supplier(
                razon_social="MediSupply Chile SpA",
                nit="76543210-K",
                representante_legal="Pedro Sánchez",
                pais="Chile",
                nombre_contacto="Laura Martínez",
                celular_contacto="+56987654321",
                certificado_filename="cert_medichile.pdf",
                certificado_path="/tmp/cert_medichile.pdf",
                email="ventas@medichile.cl",
                ciudad="Santiago",
                created_by="admin"
            )
        ]
        
        for supplier in suppliers:
            db.session.add(supplier)
        
        db.session.commit()
        print(f"✅ {len(suppliers)} proveedores de prueba creados exitosamente")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Inicializar base de datos')
    parser.add_argument('--init', action='store_true', help='Crear tablas')
    parser.add_argument('--seed', action='store_true', help='Cargar datos de prueba')
    
    args = parser.parse_args()
    
    if args.init:
        init_db()
    
    if args.seed:
        seed_data()
    
    if not args.init and not args.seed:
        print("Uso: python init_db.py [--init] [--seed]")
        print("  --init: Crear tablas")
        print("  --seed: Cargar datos de prueba")
