# Búsqueda de Inventario por Información de Producto

## Resumen de la Funcionalidad

Se ha implementado la capacidad de buscar items de inventario utilizando campos del producto (nombre, código, referencia) mediante JOINs a la tabla `products` en la base de datos compartida.

## Arquitectura

### Base de Datos Compartida

```
┌─────────────────────────────────────────────────┐
│         PostgreSQL Database (Shared)            │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐        ┌─────────────────┐  │
│  │   products   │        │ inventory_items │  │
│  ├──────────────┤        ├─────────────────┤  │
│  │ id (PK)      │◄───┐   │ id (PK)         │  │
│  │ nombre       │    └───│ product_id (FK) │  │
│  │ codigo       │        │ bodega_id       │  │
│  │ referencia   │        │ pasillo         │  │
│  │ descripcion  │        │ estanteria      │  │
│  │ categoria    │        │ nivel           │  │
│  │ ...          │        │ cantidad        │  │
│  └──────────────┘        │ ...             │  │
│                          └─────────────────┘  │
└─────────────────────────────────────────────────┘
         │                          │
         │                          │
    ┌────┴──────┐         ┌─────────┴──────┐
    │ products- │         │  inventory-    │
    │ service   │         │  service       │
    │ (5002)    │         │  (5003)        │
    └───────────┘         └────────────────┘
```

### Ventajas del Enfoque

1. **Performance**: JOINs a nivel de base de datos son más rápidos que llamadas HTTP entre microservicios
2. **Simplicidad**: No requiere implementar comunicación REST entre servicios
3. **Consistencia**: Los datos siempre están sincronizados (misma base de datos)
4. **Latencia**: Cumple con el requisito de < 1 segundo (HU-22)

## Implementación

### 1. Modelo READ-ONLY de Productos

**Archivo**: `app/modules/inventory/product_model.py`

```python
class Product(db.Model):
    """
    Modelo READ-ONLY para consultar productos desde inventory-service.
    
    IMPORTANTE: Este servicio NO debe crear, actualizar o eliminar productos.
    Solo se usa para consultas y JOINs con inventory_items.
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    codigo = db.Column(db.String(50))
    referencia = db.Column(db.String(100))
    # ... otros campos
```

### 2. Repository - Query con JOIN

**Archivo**: `app/modules/inventory/repository.py`

```python
def search_by_product_name_or_code(
    self, 
    search_query: str, 
    bodega_id: Optional[int] = None
) -> List[Tuple[InventoryItem, Product]]:
    """
    Busca items de inventario por nombre, código o referencia del producto.
    
    Utiliza JOIN con la tabla products para buscar por campos de producto.
    """
    pattern = f"%{search_query.lower()}%"
    
    query = db.session.query(InventoryItem, Product).join(
        Product, 
        InventoryItem.product_id == Product.id
    )
    
    # Filtrar por nombre, código o referencia (case-insensitive)
    query = query.filter(
        or_(
            func.lower(Product.nombre).like(pattern),
            func.lower(Product.codigo).like(pattern),
            func.lower(Product.referencia).like(pattern)
        )
    )
    
    # Filtros adicionales
    query = query.filter(
        Product.status == 'active',
        Product.is_deleted == False,
        InventoryItem.cantidad > 0
    )
    
    # Filtrar por bodega si se proporciona
    if bodega_id:
        query = query.filter(InventoryItem.bodega_id == bodega_id)
    
    # Ordenar resultados
    query = query.order_by(
        Product.nombre,
        InventoryItem.bodega_id,
        InventoryItem.pasillo
    )
    
    return query.all()
```

### 3. Service - Enriquecimiento de Datos

**Archivo**: `app/modules/inventory/service.py`

```python
def search_by_product_query(
    self, 
    search_query: str, 
    bodega_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Busca inventario por nombre, código o referencia del producto.
    Retorna datos enriquecidos con información del producto.
    """
    # Validación
    if len(search_query) < 2:
        raise BusinessError("El término de búsqueda debe tener al menos 2 caracteres")
    
    # Buscar usando JOIN
    results = self.repository.search_by_product_name_or_code(
        search_query, 
        bodega_id
    )
    
    # Enriquecer resultados con información del producto
    enriched_results = []
    for item, product in results:
        item_dict = item.to_dict()
        
        # Agregar información del producto
        item_dict['product_info'] = {
            'nombre': product.nombre,
            'codigo': product.codigo,
            'referencia': product.referencia,
            'descripcion': product.descripcion,
            'categoria': product.categoria,
            'unidad_medida': product.unidad_medida,
            'proveedor': product.proveedor
        }
        
        enriched_results.append(item_dict)
    
    return enriched_results
```

### 4. Controller - Endpoint HTTP

**Archivo**: `app/modules/inventory/controller.py`

```python
def search_by_product(self):
    """
    GET /api/v1/inventory/search-product?q=<query>&bodega_id=<id>
    
    Busca inventario por nombre, código o referencia del producto.
    """
    search_query = request.args.get('q', '').strip()
    bodega_id = request.args.get('bodega_id', type=int)
    
    # Validaciones
    if not search_query:
        return error_response(
            message='Debe proporcionar un término de búsqueda (parámetro "q")',
            status_code=400
        )
    
    if len(search_query) < 2:
        return error_response(
            message='El término de búsqueda debe tener al menos 2 caracteres',
            status_code=400
        )
    
    # Ejecutar búsqueda
    results = self.service.search_by_product_query(search_query, bodega_id)
    
    return success_response(
        data=results,
        message=f'{len(results)} producto(s) encontrado(s) en inventario'
    )
```

### 5. Routes - Endpoint Registration

**Archivo**: `app/modules/inventory/routes.py`

```python
@inventory_bp.route('/search-product', methods=['GET'])
@require_auth
def search_by_product():
    """
    Buscar inventario por nombre, código o referencia del producto.
    
    Query params:
    - q: término de búsqueda (mínimo 2 caracteres)
    - bodega_id: filtrar por bodega específica (opcional)
    """
    return controller.search_by_product()
```

## Ejemplos de Uso

### 1. Buscar por Nombre de Producto

```bash
curl "http://localhost:5003/api/v1/inventory/search-product?q=paracetamol" \
  -H "Authorization: Bearer <token>"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "1 producto(s) encontrado(s) en inventario",
  "data": [
    {
      "id": 1,
      "product_id": 5,
      "bodega_id": 1,
      "bodega_nombre": "Bodega Principal",
      "pasillo": "A",
      "estanteria": "2",
      "nivel": "3",
      "cantidad": "100.00",
      "cantidad_disponible": "80.00",
      "lote": "L-2024-001",
      "fecha_vencimiento": "2025-12-31",
      "product_info": {
        "nombre": "Paracetamol 500mg",
        "codigo": "MED-001",
        "referencia": "REF-PARA-500",
        "descripcion": "Analgésico y antipirético",
        "categoria": "Medicamentos",
        "unidad_medida": "tableta",
        "proveedor": "Farmacéutica XYZ"
      }
    }
  ]
}
```

### 2. Buscar por Código

```bash
curl "http://localhost:5003/api/v1/inventory/search-product?q=MED-001" \
  -H "Authorization: Bearer <token>"
```

### 3. Buscar por Referencia

```bash
curl "http://localhost:5003/api/v1/inventory/search-product?q=REF-PARA" \
  -H "Authorization: Bearer <token>"
```

### 4. Buscar y Filtrar por Bodega

```bash
curl "http://localhost:5003/api/v1/inventory/search-product?q=ibuprofeno&bodega_id=1" \
  -H "Authorization: Bearer <token>"
```

## Características

✅ **Búsqueda Case-Insensitive**: Los términos de búsqueda no distinguen mayúsculas/minúsculas  
✅ **Búsqueda Parcial**: Usa LIKE con wildcards (`%paracet%`)  
✅ **Multi-campo**: Busca en nombre, código Y referencia simultáneamente  
✅ **Filtro por Bodega**: Opcional, permite limitar resultados a una bodega específica  
✅ **Solo Productos Activos**: Filtra automáticamente productos inactivos o eliminados  
✅ **Solo Items con Stock**: No muestra items con cantidad = 0  
✅ **Datos Enriquecidos**: Incluye información completa del producto en cada resultado  
✅ **Performance Optimizada**: JOINs eficientes con índices en ambas tablas  

## Validaciones

- **Mínimo 2 caracteres**: El término de búsqueda debe tener al menos 2 caracteres
- **Query requerido**: El parámetro `q` es obligatorio
- **Bodega opcional**: El filtro por bodega_id es opcional
- **Autenticación**: Requiere token JWT válido

## Performance

- **Tiempo esperado**: < 500ms para búsquedas típicas
- **Índices utilizados**:
  - `idx_product_bodega` en inventory_items (product_id, bodega_id)
  - Índices en products.nombre, products.codigo
- **Optimizaciones**:
  - JOIN a nivel de base de datos (más rápido que HTTP)
  - Filtros antes del ORDER BY
  - Solo trae productos activos con stock

## Casos de Uso

1. **Operador de bodega busca producto por nombre**:
   - "Necesito encontrar dónde está el paracetamol"
   - Búsqueda: `?q=paracet`
   - Resultado: Todas las ubicaciones con paracetamol en stock

2. **Validación de código de barras**:
   - Scanner lee código `MED-001`
   - Búsqueda: `?q=MED-001`
   - Resultado: Ubicaciones exactas del producto

3. **Búsqueda por referencia del proveedor**:
   - Proveedor envía factura con referencia `REF-PARA-500`
   - Búsqueda: `?q=REF-PARA-500`
   - Resultado: Items en inventario con esa referencia

4. **Localización en bodega específica**:
   - "¿Tenemos ibuprofeno en la bodega 1?"
   - Búsqueda: `?q=ibuprofeno&bodega_id=1`
   - Resultado: Solo items en bodega 1

## Mantenimiento

### ⚠️ IMPORTANTE: Modelo Product es READ-ONLY

Este servicio **NO DEBE**:
- ❌ Crear productos (usar products-service)
- ❌ Actualizar productos (usar products-service)
- ❌ Eliminar productos (usar products-service)
- ❌ Modificar precios (usar products-service)

Este servicio **SÍ PUEDE**:
- ✅ Leer información de productos (SELECT)
- ✅ Hacer JOINs con inventory_items
- ✅ Usar datos de productos para búsquedas y reportes

### Sincronización de Datos

Como ambos servicios comparten la misma base de datos:
- Los cambios en `products` son inmediatamente visibles en `inventory-service`
- No hay problemas de sincronización
- No hay cache que invalidar
- Los datos siempre están actualizados

## Testing

```bash
# Test unitario del repository
pytest tests/test_inventory_repository.py::test_search_by_product_name_or_code

# Test de integración del endpoint
pytest tests/test_inventory_search.py::test_search_by_product_endpoint

# Test de performance
pytest tests/test_search_performance.py::test_product_search_performance
```

## Próximas Mejoras

- [ ] Agregar búsqueda por descripción de producto
- [ ] Implementar paginación en resultados
- [ ] Agregar cache para búsquedas frecuentes
- [ ] Implementar búsqueda fuzzy (búsqueda aproximada)
- [ ] Agregar filtros adicionales (categoría, proveedor)
- [ ] Exportar resultados de búsqueda a Excel/CSV

---

**Fecha de Implementación**: Enero 2025  
**Desarrollador**: Inventory Service Team  
**Versión**: 1.0.0
