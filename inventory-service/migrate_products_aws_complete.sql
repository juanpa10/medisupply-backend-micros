-- ===============================================================
-- SCRIPT DE MIGRACIÓN COMPLETO PARA MÓDULO DE PRODUCTOS
-- Base de datos: PostgreSQL
-- Fecha: Noviembre 2025
-- Descripción: Migración completa para implementar el módulo 
--              de productos con gestión de archivos
-- ===============================================================

-- ===============================================================
-- 1. MIGRACIÓN DE TABLA PRODUCTS (Agregar nuevas columnas)
-- ===============================================================

-- Verificar si la tabla products existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products') THEN
        RAISE EXCEPTION 'La tabla products no existe. Este script requiere que la tabla products ya exista.';
    END IF;
END $$;

-- Agregar nuevas columnas a la tabla products
ALTER TABLE products ADD COLUMN IF NOT EXISTS categoria_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS unidad_medida_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS proveedor_id INTEGER;
ALTER TABLE products ADD COLUMN IF NOT EXISTS precio_compra NUMERIC(12,2);

-- Campos de control de documentos requeridos
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_ficha_tecnica BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_condiciones_almacenamiento BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS requiere_certificaciones_sanitarias BOOLEAN DEFAULT false;

-- Campos de estado de documentos
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_ficha_tecnica BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_condiciones_almacenamiento BOOLEAN DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS tiene_certificaciones_sanitarias BOOLEAN DEFAULT false;

-- Campo de disponibilidad en catálogo
ALTER TABLE products ADD COLUMN IF NOT EXISTS disponible_catalogo BOOLEAN DEFAULT false;

-- Campos de auditoría (si no existen)
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS created_by VARCHAR(100) DEFAULT 'system';
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE products ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100);

-- ===============================================================
-- 2. CREACIÓN DE TABLAS DE REFERENCIA
-- ===============================================================

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT false
);

-- Tabla de unidades de medida
CREATE TABLE IF NOT EXISTS unidades_medida (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    simbolo VARCHAR(10) NOT NULL UNIQUE,
    descripcion TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT false
);

-- Tabla de proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    razon_social VARCHAR(200),
    nit VARCHAR(50) UNIQUE,
    telefono VARCHAR(50),
    email VARCHAR(100),
    direccion TEXT,
    contacto_principal VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT false
);

-- ===============================================================
-- 3. CREACIÓN DE TABLA PRODUCT_FILES
-- ===============================================================

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
    is_deleted BOOLEAN DEFAULT false,
    
    -- Constraints
    CONSTRAINT chk_file_size CHECK (file_size_bytes > 0),
    CONSTRAINT chk_file_category CHECK (file_category IN ('technical_sheet', 'storage_conditions', 'health_certifications')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'deleted', 'archived'))
);

-- ===============================================================
-- 4. CREACIÓN DE ÍNDICES
-- ===============================================================

-- Índices para tabla products
CREATE INDEX IF NOT EXISTS idx_products_categoria ON products(categoria_id);
CREATE INDEX IF NOT EXISTS idx_products_proveedor ON products(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_products_unidad ON products(unidad_medida_id);
CREATE INDEX IF NOT EXISTS idx_products_nombre ON products(nombre);
CREATE INDEX IF NOT EXISTS idx_products_codigo ON products(codigo);
CREATE INDEX IF NOT EXISTS idx_products_disponible_catalogo ON products(disponible_catalogo);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);

-- Índices para tabla product_files
CREATE INDEX IF NOT EXISTS idx_product_files_product_id ON product_files(product_id);
CREATE INDEX IF NOT EXISTS idx_product_files_category ON product_files(file_category);
CREATE INDEX IF NOT EXISTS idx_product_files_status ON product_files(status);
CREATE INDEX IF NOT EXISTS idx_product_file_category ON product_files(product_id, file_category);

-- Índices para tablas de referencia
CREATE INDEX IF NOT EXISTS idx_categorias_nombre ON categorias(nombre);
CREATE INDEX IF NOT EXISTS idx_categorias_status ON categorias(status);
CREATE INDEX IF NOT EXISTS idx_unidades_medida_simbolo ON unidades_medida(simbolo);
CREATE INDEX IF NOT EXISTS idx_unidades_medida_status ON unidades_medida(status);
CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON proveedores(nombre);
CREATE INDEX IF NOT EXISTS idx_proveedores_nit ON proveedores(nit);
CREATE INDEX IF NOT EXISTS idx_proveedores_status ON proveedores(status);

-- ===============================================================
-- 5. CREACIÓN DE FOREIGN KEYS
-- ===============================================================

-- Foreign keys para tabla products (solo si las tablas de referencia existen)
DO $$
BEGIN
    -- FK hacia categorias
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categorias') THEN
        BEGIN
            ALTER TABLE products ADD CONSTRAINT fk_products_categoria 
            FOREIGN KEY (categoria_id) REFERENCES categorias(id);
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END;
    END IF;
    
    -- FK hacia unidades_medida
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'unidades_medida') THEN
        BEGIN
            ALTER TABLE products ADD CONSTRAINT fk_products_unidad 
            FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id);
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END;
    END IF;
    
    -- FK hacia proveedores
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'proveedores') THEN
        BEGIN
            ALTER TABLE products ADD CONSTRAINT fk_products_proveedor 
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id);
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END;
    END IF;
END $$;

-- Foreign key para tabla product_files
DO $$
BEGIN
    BEGIN
        ALTER TABLE product_files ADD CONSTRAINT fk_product_files_product 
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END;
END $$;

-- ===============================================================
-- 6. INSERCIÓN DE DATOS DE REFERENCIA
-- ===============================================================

-- Datos de muestra para categorías
INSERT INTO categorias (nombre, descripcion) VALUES
    ('Medicamentos', 'Productos farmacéuticos y medicamentos'),
    ('Suministros Médicos', 'Equipos y suministros médicos'),
    ('Dispositivos Médicos', 'Dispositivos y equipos médicos especializados'),
    ('Material Quirúrgico', 'Material para procedimientos quirúrgicos'),
    ('Primeros Auxilios', 'Productos para primeros auxilios')
ON CONFLICT (nombre) DO NOTHING;

-- Datos de muestra para unidades de medida
INSERT INTO unidades_medida (nombre, simbolo, descripcion) VALUES
    ('Unidades', 'uds', 'Cantidad en unidades individuales'),
    ('Kilogramos', 'kg', 'Peso en kilogramos'),
    ('Gramos', 'g', 'Peso en gramos'),
    ('Litros', 'L', 'Volumen en litros'),
    ('Mililitros', 'ml', 'Volumen en mililitros'),
    ('Metros', 'm', 'Longitud en metros'),
    ('Centímetros', 'cm', 'Longitud en centímetros'),
    ('Cajas', 'caja', 'Empaque en cajas'),
    ('Miligramos', 'mg', 'Peso en miligramos'),
    ('Microgramos', 'mcg', 'Peso en microgramos')
ON CONFLICT (nombre) DO NOTHING;

-- Datos de muestra para proveedores
INSERT INTO proveedores (nombre, razon_social, nit, telefono, email, contacto_principal) VALUES
    ('Laboratorios ABC', 'Laboratorios ABC S.A.S.', '900123456-1', '+57-1-234-5678', 'contacto@labsabc.com', 'Juan Pérez'),
    ('MedSupply Corp', 'Medical Supply Corporation S.A.', '800987654-2', '+57-1-987-6543', 'ventas@medsupply.com', 'Ana García'),
    ('FarmaColombia', 'Farmacéutica Colombia Ltda.', '700456789-3', '+57-1-456-7890', 'info@farmacolombia.co', 'Carlos López'),
    ('Equipos Médicos del Sur', 'Equipos Médicos del Sur S.A.S.', '600321654-4', '+57-2-321-6540', 'contacto@equiposmedicos.com', 'María Rodríguez'),
    ('Distribuidora Nacional', 'Distribuidora Nacional de Medicamentos S.A.', '500789123-5', '+57-1-789-1230', 'distribucion@dnm.com', 'Pedro Martínez'),
    ('Farmacéuticos Unidos S.A.', 'Farmacéuticos Unidos Sociedad Anónima', '400654987-6', '+57-3-654-9870', 'unidos@farmaceuticos.co', 'Laura Gómez')
ON CONFLICT (nit) DO NOTHING;

-- ===============================================================
-- 7. ACTUALIZACIÓN DE DATOS EXISTENTES (OPCIONAL)
-- ===============================================================

-- Actualizar productos existentes para que tengan valores por defecto válidos
UPDATE products 
SET 
    categoria_id = 1,
    unidad_medida_id = 1,
    proveedor_id = 1,
    precio_compra = COALESCE(precio, 0),
    requiere_ficha_tecnica = false,
    requiere_condiciones_almacenamiento = false,
    requiere_certificaciones_sanitarias = false,
    tiene_ficha_tecnica = false,
    tiene_condiciones_almacenamiento = false,
    tiene_certificaciones_sanitarias = false,
    disponible_catalogo = false,
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    created_by = COALESCE(created_by, 'migration')
WHERE categoria_id IS NULL;

-- ===============================================================
-- 8. VERIFICACIONES FINALES
-- ===============================================================

-- Verificar estructura de tabla products
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns 
    WHERE table_name = 'products' 
    AND column_name IN ('categoria_id', 'unidad_medida_id', 'proveedor_id', 'precio_compra');
    
    IF column_count < 4 THEN
        RAISE EXCEPTION 'Error: No todas las columnas fueron agregadas a la tabla products';
    END IF;
    
    RAISE NOTICE 'Verificación exitosa: Todas las columnas agregadas a products';
END $$;

-- Verificar que las tablas de referencia existen
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'categorias') THEN
        RAISE EXCEPTION 'Error: Tabla categorias no fue creada';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'unidades_medida') THEN
        RAISE EXCEPTION 'Error: Tabla unidades_medida no fue creada';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'proveedores') THEN
        RAISE EXCEPTION 'Error: Tabla proveedores no fue creada';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product_files') THEN
        RAISE EXCEPTION 'Error: Tabla product_files no fue creada';
    END IF;
    
    RAISE NOTICE 'Verificación exitosa: Todas las tablas fueron creadas';
END $$;

-- Verificar datos de referencia
DO $$
DECLARE
    categoria_count INTEGER;
    unidad_count INTEGER;
    proveedor_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO categoria_count FROM categorias WHERE status = 'active';
    SELECT COUNT(*) INTO unidad_count FROM unidades_medida WHERE status = 'active';
    SELECT COUNT(*) INTO proveedor_count FROM proveedores WHERE status = 'active';
    
    RAISE NOTICE 'Datos insertados - Categorías: %, Unidades: %, Proveedores: %', 
                 categoria_count, unidad_count, proveedor_count;
END $$;

-- ===============================================================
-- SCRIPT COMPLETADO EXITOSAMENTE
-- ===============================================================

-- Mostrar resumen final
SELECT 
    'MIGRACIÓN COMPLETADA' as status,
    CURRENT_TIMESTAMP as fecha_finalizacion,
    'Módulo de productos listo para uso' as mensaje;

-- Mostrar estructura final de la tabla products (columnas principales)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'products' 
  AND column_name IN ('id', 'nombre', 'codigo', 'categoria_id', 'unidad_medida_id', 
                      'proveedor_id', 'precio_compra', 'precio_venta', 
                      'requiere_ficha_tecnica', 'disponible_catalogo')
ORDER BY ordinal_position;