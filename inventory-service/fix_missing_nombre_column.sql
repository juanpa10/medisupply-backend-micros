-- ===============================================================
-- SCRIPT PARA AGREGAR LA COLUMNA 'nombre' FALTANTE
-- ===============================================================

-- Agregar la columna nombre que faltó en la migración anterior
ALTER TABLE products ADD COLUMN IF NOT EXISTS nombre VARCHAR(200);

-- Migrar datos de name a nombre
UPDATE products SET nombre = name WHERE nombre IS NULL;

-- Verificar que funcionó
SELECT COUNT(*) as productos_con_nombre FROM products WHERE nombre IS NOT NULL;

-- Mostrar algunos ejemplos
SELECT name, nombre FROM products LIMIT 5;