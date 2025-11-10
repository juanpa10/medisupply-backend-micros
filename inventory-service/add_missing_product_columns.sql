-- ===============================================================
-- SCRIPT RÁPIDO: AGREGAR COLUMNAS FALTANTES PARA PRODUCTS
-- ===============================================================

-- Agregar todas las columnas que espera el modelo SQLAlchemy
ALTER TABLE products ADD COLUMN IF NOT EXISTS categoria_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unidad_medida_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS proveedor_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS precio_compra NUMERIC(12,2);

-- Campos de control de documentos
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_ficha_tecnica BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_condiciones_almacenamiento BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_certificaciones_sanitarias BOOLEAN DEFAULT false;

-- Campos de auditoría que pueden estar faltando
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_by VARCHAR(100) DEFAULT 'system';
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100);

-- Actualizar valores por defecto para evitar errores NULL
UPDATE products SET 
    categoria_id = 1,
    unidad_medida_id = 1,
    proveedor_id = 1,
    precio_compra = COALESCE(precio_venta, 0),
    requiere_ficha_tecnica = false,
    requiere_condiciones_almacenamiento = false,
    requiere_certificaciones_sanitarias = false,
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    created_by = COALESCE(created_by, 'migration')
WHERE categoria_id IS NULL;

-- Verificar columnas agregadas
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'products' 
  AND column_name IN ('categoria_id', 'unidad_medida_id', 'proveedor_id', 
                      'precio_compra', 'requiere_ficha_tecnica')
ORDER BY column_name;