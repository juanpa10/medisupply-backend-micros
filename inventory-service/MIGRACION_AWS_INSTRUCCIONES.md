# 🗃️ Scripts de Migración para Base de Datos AWS

## Archivos Creados

### 1. `migrate_products_aws_complete.sql` (RECOMENDADO)
**Migración completa** que incluye:
- ✅ Migración de tabla `products` con todas las columnas nuevas
- ✅ Creación de tablas de referencia (`categorias`, `unidades_medida`, `proveedores`)
- ✅ Creación de tabla `product_files` para gestión de archivos
- ✅ Todos los índices y foreign keys
- ✅ Datos de muestra para las tablas de referencia
- ✅ Verificaciones de integridad y validaciones

### 2. `migrate_products_basic.sql`
**Migración básica** que incluye solo:
- ✅ Columnas nuevas en tabla `products`
- ✅ Tabla `product_files`
- ✅ Índices esenciales
- ❌ Sin tablas de referencia
- ❌ Sin datos de muestra

## 🚀 Instrucciones de Uso

### Opción A: Migración Completa (Recomendada)

```bash
# Conectarse a la base de datos AWS
psql -h [tu-endpoint-aws] -U [usuario] -d [base-datos]

# Ejecutar el script completo
\i migrate_products_aws_complete.sql

# Verificar que todo esté bien
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('products', 'categorias', 'unidades_medida', 'proveedores', 'product_files');
```

### Opción B: Migración Básica

```bash
# Solo si ya tienes las tablas de referencia o no las necesitas
\i migrate_products_basic.sql
```

### Opción C: Ejecución por Línea de Comandos

```bash
# Para el script completo
psql -h [endpoint] -U [usuario] -d [base-datos] -f migrate_products_aws_complete.sql

# Para el script básico
psql -h [endpoint] -U [usuario] -d [base-datos] -f migrate_products_basic.sql
```

## 🔍 Verificaciones Post-Migración

### 1. Verificar Columnas en Products
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'products' 
  AND column_name LIKE '%categoria%' OR column_name LIKE '%precio%'
ORDER BY column_name;
```

### 2. Verificar Tablas Creadas
```sql
SELECT table_name, table_type
FROM information_schema.tables 
WHERE table_name IN ('categorias', 'unidades_medida', 'proveedores', 'product_files')
ORDER BY table_name;
```

### 3. Verificar Datos de Referencia
```sql
SELECT 
    (SELECT COUNT(*) FROM categorias) as categorias_count,
    (SELECT COUNT(*) FROM unidades_medida) as unidades_count,
    (SELECT COUNT(*) FROM proveedores) as proveedores_count;
```

### 4. Probar Creación de Producto
```sql
-- Insertar un producto de prueba
INSERT INTO products (
    nombre, codigo, descripcion, categoria_id, unidad_medida_id, 
    proveedor_id, precio_compra, precio_venta
) VALUES (
    'Producto de Prueba', 'TEST-001', 'Producto para verificar migración',
    1, 1, 1, 100.00, 120.00
);

-- Verificar que se insertó
SELECT id, nombre, codigo, categoria_id, unidad_medida_id, proveedor_id
FROM products WHERE codigo = 'TEST-001';
```

## ⚠️ Consideraciones Importantes

### Antes de Ejecutar
- ✅ **Hacer backup** de la base de datos
- ✅ Verificar que la tabla `products` existe
- ✅ Verificar permisos para crear tablas e índices
- ✅ Revisar el espacio en disco disponible

### Durante la Ejecución
- ⏳ El script puede tardar varios minutos en bases grandes
- 📊 Observar los mensajes de verificación
- ❌ Si hay errores, revisar los logs

### Después de la Ejecución
- ✅ Verificar que todas las tablas fueron creadas
- ✅ Comprobar que los datos de referencia están presentes
- ✅ Probar la creación de un producto de prueba
- ✅ Validar que el API funciona correctamente

## 🐛 Resolución de Problemas

### Error: "relation does not exist"
- La tabla `products` no existe o no tienes permisos
- Verificar nombre correcto de la tabla

### Error: "permission denied"
- Necesitas permisos de CREATE TABLE y ALTER TABLE
- Contactar al administrador de la BD

### Error: "column already exists"
- Algunas columnas ya existen, esto es normal
- El script usa `IF NOT EXISTS` para evitar errores

### Error: "constraint already exists"
- Las foreign keys ya existen, esto es normal
- El script maneja duplicados automáticamente

## 📋 Checklist Post-Migración

- [ ] Tabla `products` tiene las nuevas columnas
- [ ] Tabla `product_files` fue creada
- [ ] Tablas de referencia tienen datos
- [ ] Índices fueron creados
- [ ] Foreign keys funcionan
- [ ] Producto de prueba se puede crear
- [ ] API responde correctamente
- [ ] Postman collection funciona

## 🆘 Contacto y Soporte

Si encuentras algún problema:

1. **Revisar logs** del script de migración
2. **Verificar permisos** en la base de datos  
3. **Comprobar espacio** en disco
4. **Validar sintaxis** SQL para tu versión de PostgreSQL

---

**¡Migración lista para producción!** 🚀