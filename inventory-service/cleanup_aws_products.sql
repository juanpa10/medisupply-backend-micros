-- ===============================================================
-- SCRIPT DE LIMPIEZA Y NORMALIZACIÓN BD PRODUCTOS AWS
-- ===============================================================

-- ===============================================================
-- PASO 1: ANÁLISIS DE DUPLICADOS
-- ===============================================================

-- Ver cuántos duplicados hay por producto
SELECT nombre, COUNT(*) as cantidad_duplicados 
FROM products 
GROUP BY nombre 
HAVING COUNT(*) > 1
ORDER BY cantidad_duplicados DESC;

-- Ver el total de productos únicos vs total de registros
SELECT 
    COUNT(DISTINCT nombre) as productos_unicos,
    COUNT(*) as total_registros,
    COUNT(*) - COUNT(DISTINCT nombre) as registros_duplicados
FROM products;

-- ===============================================================
-- PASO 2: COMPLETAR MIGRACIÓN DE DATOS FALTANTES
-- ===============================================================

-- Actualizar codigo y referencia que están NULL
UPDATE products SET 
    codigo = code,
    referencia = reference
WHERE (codigo IS NULL OR referencia IS NULL) 
  AND (code IS NOT NULL OR reference IS NOT NULL);

-- Verificar migración
SELECT COUNT(*) as productos_sin_codigo FROM products WHERE codigo IS NULL;

-- ===============================================================
-- PASO 3: ELIMINAR DUPLICADOS INTELIGENTEMENTE
-- ===============================================================

-- Crear una tabla temporal con productos únicos (conservar el de menor ID)
CREATE TEMP TABLE productos_unicos AS
SELECT DISTINCT ON (nombre) 
    id, nombre, codigo, referencia, descripcion, precio_venta, status
FROM products 
WHERE nombre IS NOT NULL
ORDER BY nombre, id ASC;

-- Ver cuántos productos únicos tendremos
SELECT COUNT(*) as productos_que_se_conservaran FROM productos_unicos;

-- ===============================================================
-- PASO 4: RESPALDO ANTES DE ELIMINAR
-- ===============================================================

-- Crear tabla de respaldo con todos los productos actuales
CREATE TABLE products_backup_$(date '+%Y%m%d') AS 
SELECT * FROM products;

-- ===============================================================
-- PASO 5: ELIMINACIÓN DE DUPLICADOS
-- ===============================================================

-- OPCIÓN A: Eliminar duplicados conservando el de menor ID
DELETE FROM products 
WHERE id NOT IN (
    SELECT DISTINCT ON (nombre) id
    FROM products 
    WHERE nombre IS NOT NULL
    ORDER BY nombre, id ASC
);

-- ===============================================================
-- PASO 6: VERIFICACIONES FINALES
-- ===============================================================

-- Contar productos finales
SELECT COUNT(*) as total_productos_finales FROM products;

-- Ver productos únicos
SELECT nombre, codigo, referencia, precio_venta, status, created_at 
FROM products 
ORDER BY nombre 
LIMIT 10;

-- Verificar que no hay duplicados
SELECT nombre, COUNT(*) as cantidad 
FROM products 
GROUP BY nombre 
HAVING COUNT(*) > 1;

-- ===============================================================
-- PASO 7: ACTUALIZAR SECUENCIA DE IDs
-- ===============================================================

-- Resetear la secuencia de IDs para que siga desde el máximo actual
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));

-- ===============================================================
-- FINALIZACIÓN
-- ===============================================================

SELECT 
    'LIMPIEZA COMPLETADA' as status,
    COUNT(*) as productos_finales,
    COUNT(DISTINCT nombre) as productos_unicos
FROM products;