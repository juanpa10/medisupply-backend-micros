-- ===============================================================
-- SCRIPT DE MIGRACIÓN: NOMBRES DE COLUMNAS EN TABLA PRODUCTS
-- Fecha: Noviembre 2025
-- Descripción: Agregar columnas en español para compatibilidad con 
--              el módulo de productos que usa nombres en español
-- ===============================================================

-- ===============================================================
-- PASO 1: AGREGAR COLUMNAS EN ESPAÑOL
-- ===============================================================

-- Agregar columnas equivalentes en español
ALTER TABLE products ADD COLUMN IF NOT EXISTS nombre VARCHAR(200);
ALTER TABLE products ADD COLUMN IF NOT EXISTS codigo VARCHAR(50);
ALTER TABLE products ADD COLUMN IF NOT EXISTS referencia VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS precio_venta NUMERIC(10,2);

-- ===============================================================
-- PASO 2: MIGRAR DATOS EXISTENTES DE INGLÉS A ESPAÑOL
-- ===============================================================

-- Copiar datos de columnas en inglés a columnas en español
UPDATE products SET 
    nombre = name,
    codigo = code,
    referencia = reference,
    descripcion = description,
    precio_venta = unit_price
WHERE nombre IS NULL;

-- ===============================================================
-- PASO 3: AGREGAR COLUMNA is_deleted SI NO EXISTE
-- ===============================================================

ALTER TABLE products ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT false;

-- Actualizar registros existentes que podrían no tener valor
UPDATE products SET is_deleted = false WHERE is_deleted IS NULL;

-- ===============================================================
-- PASO 4: VERIFICACIONES
-- ===============================================================

-- Verificar que las columnas fueron creadas
DO $$
DECLARE
    missing_columns TEXT := '';
BEGIN
    -- Verificar nombre
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'nombre') THEN
        missing_columns := missing_columns || 'nombre, ';
    END IF;
    
    -- Verificar codigo
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'codigo') THEN
        missing_columns := missing_columns || 'codigo, ';
    END IF;
    
    -- Verificar referencia
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'referencia') THEN
        missing_columns := missing_columns || 'referencia, ';
    END IF;
    
    -- Verificar descripcion
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'descripcion') THEN
        missing_columns := missing_columns || 'descripcion, ';
    END IF;
    
    -- Verificar precio_venta
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'precio_venta') THEN
        missing_columns := missing_columns || 'precio_venta, ';
    END IF;
    
    -- Verificar is_deleted
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'is_deleted') THEN
        missing_columns := missing_columns || 'is_deleted, ';
    END IF;
    
    IF LENGTH(missing_columns) > 0 THEN
        RAISE EXCEPTION 'Columnas faltantes: %', RTRIM(missing_columns, ', ');
    ELSE
        RAISE NOTICE '✅ Todas las columnas en español fueron creadas exitosamente';
    END IF;
END $$;

-- ===============================================================
-- PASO 5: VERIFICAR MIGRACIÓN DE DATOS
-- ===============================================================

-- Contar registros con datos migrados
DO $$
DECLARE
    total_products INTEGER;
    migrated_products INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_products FROM products;
    SELECT COUNT(*) INTO migrated_products FROM products WHERE nombre IS NOT NULL;
    
    RAISE NOTICE 'Total de productos: %', total_products;
    RAISE NOTICE 'Productos con nombre migrado: %', migrated_products;
    
    IF total_products > 0 AND migrated_products = 0 THEN
        RAISE WARNING '⚠️ Los datos no se migraron correctamente';
    ELSIF migrated_products > 0 THEN
        RAISE NOTICE '✅ Migración de datos exitosa: % productos actualizados', migrated_products;
    ELSE
        RAISE NOTICE 'ℹ️ No hay productos para migrar';
    END IF;
END $$;

-- ===============================================================
-- PASO 6: CREAR ÍNDICES PARA LAS NUEVAS COLUMNAS
-- ===============================================================

CREATE INDEX IF NOT EXISTS idx_products_nombre ON products(nombre);
CREATE INDEX IF NOT EXISTS idx_products_codigo ON products(codigo);
CREATE INDEX IF NOT EXISTS idx_products_referencia ON products(referencia);
CREATE INDEX IF NOT EXISTS idx_products_is_deleted ON products(is_deleted);

-- ===============================================================
-- FINALIZACIÓN
-- ===============================================================

SELECT 
    '✅ MIGRACIÓN DE COLUMNAS COMPLETADA' as status,
    CURRENT_TIMESTAMP as fecha_finalizacion,
    'Columnas en español agregadas y datos migrados' as mensaje;

-- Mostrar estructura actual de la tabla products
SELECT 
    column_name, 
    data_type,
    CASE WHEN is_nullable = 'YES' THEN 'NULL' ELSE 'NOT NULL' END as nullable
FROM information_schema.columns 
WHERE table_name = 'products' 
  AND column_name IN ('name', 'nombre', 'code', 'codigo', 'reference', 'referencia', 
                      'description', 'descripcion', 'unit_price', 'precio_venta', 'is_deleted')
ORDER BY 
    CASE column_name
        WHEN 'name' THEN 1
        WHEN 'nombre' THEN 2
        WHEN 'code' THEN 3
        WHEN 'codigo' THEN 4
        WHEN 'reference' THEN 5
        WHEN 'referencia' THEN 6
        WHEN 'description' THEN 7
        WHEN 'descripcion' THEN 8
        WHEN 'unit_price' THEN 9
        WHEN 'precio_venta' THEN 10
        WHEN 'is_deleted' THEN 11
    END;