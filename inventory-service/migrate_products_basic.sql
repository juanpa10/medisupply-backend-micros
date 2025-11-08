-- ===============================================================
-- MIGRACIÓN RÁPIDA - SOLO TABLA PRODUCTS
-- Para usar cuando las tablas de referencia ya existen o no son necesarias
-- ===============================================================

-- 1. Agregar columnas faltantes a products
ALTER TABLE products ADD COLUMN IF NOT EXISTS categoria_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unidad_medida_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS proveedor_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS precio_compra NUMERIC(12,2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_ficha_tecnica BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_condiciones_almacenamiento BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_certificaciones_sanitarias BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_ficha_tecnica BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_condiciones_almacenamiento BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_certificaciones_sanitarias BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS disponible_catalogo BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_by VARCHAR(100) DEFAULT 'system';
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100);

-- 2. Crear tabla product_files
CREATE TABLE IF NOT EXISTS product_files (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    file_category VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    uploaded_by_user_id INTEGER,
    uploaded_by_username VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT false
);

-- 3. Crear índices esenciales
CREATE INDEX IF NOT EXISTS idx_products_categoria ON products(categoria_id);
CREATE INDEX IF NOT EXISTS idx_products_proveedor ON products(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_products_unidad ON products(unidad_medida_id);
CREATE INDEX IF NOT EXISTS idx_products_nombre ON products(nombre);
CREATE INDEX IF NOT EXISTS idx_products_codigo ON products(codigo);
CREATE INDEX IF NOT EXISTS idx_product_files_product_id ON product_files(product_id);
CREATE INDEX IF NOT EXISTS idx_product_files_category ON product_files(file_category);

-- 4. Agregar FK solo hacia products
ALTER TABLE product_files ADD CONSTRAINT IF NOT EXISTS fk_product_files_product 
FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;

-- Verificación
SELECT 'Migración básica completada' as status;