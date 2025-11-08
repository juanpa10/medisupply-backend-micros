#!/usr/bin/env python3
"""
Script de migración para actualizar la tabla products
"""
import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la base de datos
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://app:app@medisupply-db:5432/medisupplydb')

def run_migration():
    """Ejecuta la migración de la tabla products"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            logger.info("🔄 Iniciando migración de la tabla products...")
            
            # 1. Agregar columnas faltantes
            migration_queries = [
                # Agregar nuevas columnas
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS categoria_id INTEGER;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS unidad_medida_id INTEGER;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS proveedor_id INTEGER;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS precio_compra NUMERIC(12,2);",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_ficha_tecnica BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_condiciones_almacenamiento BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_certificaciones_sanitarias BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_ficha_tecnica BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_condiciones_almacenamiento BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_certificaciones_sanitarias BOOLEAN DEFAULT false;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS disponible_catalogo BOOLEAN DEFAULT false;",
                
                # Agregar columnas de auditoría si no existen
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS created_by VARCHAR(100) DEFAULT 'system';",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100);",
            ]
            
            for query in migration_queries:
                try:
                    conn.execute(text(query))
                    logger.info(f"✅ Ejecutado: {query[:50]}...")
                except Exception as e:
                    logger.error(f"❌ Error en query: {query[:50]}... - {e}")
            
            # 2. Crear índices
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_products_categoria ON products(categoria_id);",
                "CREATE INDEX IF NOT EXISTS idx_products_proveedor ON products(proveedor_id);",
                "CREATE INDEX IF NOT EXISTS idx_products_unidad ON products(unidad_medida_id);",
                "CREATE INDEX IF NOT EXISTS idx_products_nombre ON products(nombre);",
                "CREATE INDEX IF NOT EXISTS idx_products_codigo ON products(codigo);",
            ]
            
            for query in index_queries:
                try:
                    conn.execute(text(query))
                    logger.info(f"✅ Índice creado: {query[:50]}...")
                except Exception as e:
                    logger.error(f"❌ Error creando índice: {e}")
            
            # 3. Agregar foreign keys si las tablas maestras existen
            fk_queries = [
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categorias') THEN
                        ALTER TABLE products ADD CONSTRAINT IF NOT EXISTS fk_products_categoria 
                        FOREIGN KEY (categoria_id) REFERENCES categorias(id);
                    END IF;
                END $$;
                """,
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'unidades_medida') THEN
                        ALTER TABLE products ADD CONSTRAINT IF NOT EXISTS fk_products_unidad 
                        FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id);
                    END IF;
                END $$;
                """,
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'proveedores') THEN
                        ALTER TABLE products ADD CONSTRAINT IF NOT EXISTS fk_products_proveedor 
                        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id);
                    END IF;
                END $$;
                """
            ]
            
            for query in fk_queries:
                try:
                    conn.execute(text(query))
                    logger.info("✅ Foreign key configurada")
                except Exception as e:
                    logger.error(f"❌ Error configurando FK: {e}")
            
            # Commit cambios
            conn.commit()
            logger.info("🎉 ¡Migración completada exitosamente!")
            
            # 4. Verificar estructura final
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'products' ORDER BY column_name;"))
            columns = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Columnas finales en products: {', '.join(columns)}")
            
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        raise

if __name__ == "__main__":
    run_migration()