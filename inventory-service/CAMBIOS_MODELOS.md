# Resumen de Cambios en Modelos - Inventory Service

## Fecha: 26 de octubre de 2025

### 1. InventoryItem (models.py)

#### Campos ELIMINADOS:
- ❌ `bodega_id` - Integer, ForeignKey
- ❌ `bodega_nombre` - String(100)
- ❌ `lote` - String(50)
- ❌ `fecha_vencimiento` - Date
- ❌ `cantidad_reservada` - Numeric(10, 2)
- ❌ `cantidad_disponible` - Numeric(10, 2)
- ❌ `cantidad_minima` - Numeric(10, 2)
- ❌ `cantidad_maxima` - Numeric(10, 2)
- ❌ `costo_almacenamiento` - Numeric(10, 2)

#### Campos MANTENIDOS:
- ✅ `product_id` - Integer (relación con productos)
- ✅ `pasillo` - String(20) - Ubicación en bodega
- ✅ `estanteria` - String(20) - Ubicación en bodega
- ✅ `nivel` - String(20) - Ubicación en bodega
- ✅ `cantidad` - Numeric(10, 2) - Stock actual
- ✅ `status` - String(20) - Estado del inventario

#### Métodos ELIMINADOS:
- ❌ `is_stock_bajo()` - ya no hay cantidad_minima
- ❌ `is_stock_alto()` - ya no hay cantidad_maxima
- ❌ `get_alerta_stock()` - ya no hay alertas de stock
- ❌ `reservar_stock()` - ya no hay cantidad_reservada
- ❌ `liberar_stock()` - ya no hay cantidad_reservada

#### Métodos MANTENIDOS:
- ✅ `to_dict()` - Actualizado sin campos eliminados
- ✅ `get_ubicacion_completa()` - Formato de ubicación
- ✅ `tiene_ubicacion()` - Verifica si tiene ubicación
- ✅ `actualizar_ubicacion()` - Actualiza pasillo/estantería/nivel
- ✅ `ajustar_cantidad()` - Simplificado (solo suma/resta)

#### Índices ACTUALIZADOS:
```python
__table_args__ = (
    Index('idx_location', 'pasillo', 'estanteria', 'nivel'),  # Sin bodega_id
)
```

---

### 2. InventoryMovement (models.py)

#### Campos ELIMINADOS:
- ❌ `bodega_id` - Integer (desnormalizado)
- ❌ `lote` - String(50)

#### Campos MANTENIDOS:
- ✅ `inventory_item_id` - Integer, ForeignKey
- ✅ `product_id` - Integer (desnormalizado)
- ✅ `tipo` - String(30) - entrada/salida/ajuste
- ✅ `cantidad` - Numeric(10, 2)
- ✅ `cantidad_anterior` - Numeric(10, 2)
- ✅ `cantidad_nueva` - Numeric(10, 2)
- ✅ `motivo` - String(200)
- ✅ `documento_referencia` - String(100)
- ✅ `usuario_id` - Integer
- ✅ `usuario_nombre` - String(200)
- ✅ `fecha_movimiento` - DateTime

#### Índices ACTUALIZADOS:
```python
__table_args__ = (
    Index('idx_product_movement', 'product_id', 'fecha_movimiento'),
    Index('idx_item_movement', 'inventory_item_id', 'fecha_movimiento'),
    Index('idx_tipo_fecha', 'tipo', 'fecha_movimiento'),
    # ELIMINADO: Index('idx_bodega_fecha', 'bodega_id', 'fecha_movimiento')
)
```

---

### 3. Product (product_model.py) - READ-ONLY

#### Campos MODIFICADOS a Foreign Keys:
- 🔄 `categoria` → `categoria_id` (Integer, ForeignKey('categorias.id'))
- 🔄 `unidad_medida` → `unidad_medida_id` (Integer, ForeignKey('unidades_medida.id'))
- 🔄 `proveedor` → `proveedor_id` (Integer, ForeignKey('proveedores.id'))

#### NOTA IMPORTANTE:
Los siguientes campos ya NO se almacenan en la tabla `products`:
- ❌ `ficha_tecnica` - Ahora en tabla `files`
- ❌ `condiciones_de_almacenamiento` - Ahora en tabla `files`
- ❌ `certificaciones_sanitarias` - Ahora en tabla `files`

Estos archivos se gestionan mediante la tabla `files`:
```sql
CREATE TABLE files (
    id serial4 PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,  -- 'products'
    entity_id int4 NOT NULL,            -- product_id
    file_category VARCHAR(50) NOT NULL, -- 'technical_sheet', 'storage_conditions', 'health_certifications'
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_extension VARCHAR(10) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    description TEXT,
    tags JSONB,
    status VARCHAR(50) DEFAULT 'active',
    uploaded_by_user_id int4 NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_user_id int4,
    updated_at TIMESTAMP,
    deleted_by_user_id int4,
    deleted_at TIMESTAMP,
    CONSTRAINT chk_file_size CHECK (file_size_bytes > 0)
);
```

---

### 4. init_db.py - Datos de Muestra

#### Productos (create_sample_products):
- Actualizados con `categoria_id`, `unidad_medida_id`, `proveedor_id`
- Total: 10 productos de muestra
- IDs de categoría: 1=Medicamentos, 2=Antibióticos, 3=Cardiovascular, 4=Endocrinología, 5=Alergias
- IDs de unidad: 1=tableta, 2=cápsula
- IDs de proveedor: 1-10 (uno por cada producto)

#### Items de Inventario (create_sample_inventory_items):
- Simplificados: solo `product_id`, ubicación y `cantidad`
- Sin campos: bodega, lote, vencimiento, reservas, alertas, costos
- Total: 11 items (10 productos + 1 duplicado en otra ubicación)
- Ubicaciones: Pasillos A, B, C, D con estanterías y niveles

#### Movimientos (create_sample_movements):
- Simplificados: sin `bodega_id` y `lote`
- Total: 4 movimientos de muestra
- Tipos: ENTRADA, SALIDA, AJUSTE

---

## Impacto en Funcionalidad

### Funcionalidad ELIMINADA:
1. ❌ Gestión de múltiples bodegas/almacenes
2. ❌ Control de lotes y fechas de vencimiento
3. ❌ Reservas de stock (cantidad_reservada)
4. ❌ Alertas de stock bajo/alto (cantidad_minima/maxima)
5. ❌ Costos de almacenamiento

### Funcionalidad MANTENIDA:
1. ✅ Búsqueda de productos por ubicación (pasillo, estantería, nivel)
2. ✅ Control de cantidad en stock
3. ✅ Trazabilidad de movimientos (entradas/salidas/ajustes)
4. ✅ JOIN con tabla products para búsqueda por nombre/código
5. ✅ Estado de inventario (available, quarantine, etc.)

### Nueva Arquitectura:
1. 📁 Archivos de productos ahora en tabla `files` separada
2. 🔗 Categorías, unidades y proveedores ahora son Foreign Keys
3. 🗂️ Gestión centralizada de archivos para todos los módulos

---

## Próximos Pasos

1. ✅ Modelos actualizados
2. ⏳ **Actualizar repository.py** - Eliminar filtros por bodega_id, lote
3. ⏳ **Actualizar service.py** - Ajustar response format
4. ⏳ **Actualizar tests** - Quitar validaciones de campos eliminados
5. ⏳ **Migración de base de datos** - DROP/CREATE con nueva estructura
6. ⏳ **Documentación** - Actualizar README.md y API_DOCS.md

---

## Comandos para Reinicializar BD

```bash
# Desde inventory-service/
python init_db.py

# O desde Docker
docker-compose exec inventory-service python init_db.py
```

**ADVERTENCIA**: Esto eliminará TODOS los datos existentes y creará la nueva estructura.
