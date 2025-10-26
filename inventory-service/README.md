# Inventory Service - Sistema de Gestión de Inventario

Microservicio simplificado para la búsqueda rápida de productos en inventario del sistema MediSupply.

## 📋 Descripción

Inventory Service es un microservicio diseñado para cumplir con la **Historia de Usuario HU-22**: "Como operador logístico quiero localizar un producto en bodega en menos de un segundo".

**IMPORTANTE**: Este microservicio maneja **únicamente el inventario** (stock, ubicaciones, lotes). La información de productos (nombre, descripción, categoría, precios) se maneja en el microservicio `products-service`, con el cual comparte la misma base de datos PostgreSQL.

### Arquitectura de Microservicios

| Microservicio | Responsabilidad | Base de Datos |
|---------------|-----------------|---------------|
| **products-service** | Catálogo de productos: nombre, código, descripción, categoría, unidad de medida, proveedor, precios | PostgreSQL (tabla `products`) |
| **inventory-service** | Inventario: stock, ubicación física, lotes, fechas de vencimiento, bodegas | PostgreSQL (tablas `inventory_items`, `inventory_movements`) |

**Base de datos compartida**: Ambos microservicios usan la misma base de datos PostgreSQL para permitir JOINs eficientes entre productos e inventario.

### Características Principales

✅ **Búsqueda ultra-rápida** (< 1 segundo) por nombre, código o referencia de producto  
✅ **Localización exacta** en bodega (pasillo, estantería, nivel)  
✅ **JOIN optimizado** entre productos e inventario para respuestas completas  
✅ **API simplificada** con un solo endpoint de búsqueda  
✅ **Autenticación JWT** integrada con auth-service  
✅ **Tests comprehensivos** con pytest (11 tests, 100% aprobación)  
✅ **Dockerizado** para fácil despliegue

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker >= 20.10
- Docker Compose >= 1.29
- Python 3.11+ (para desarrollo local)
- PostgreSQL 15+

### Instalación con Docker

```bash
# 1. Clonar el repositorio
cd inventory-service

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar servicios
docker-compose up -d

# 4. Inicializar base de datos
docker-compose exec inventory-service python init_db.py

# 5. Verificar servicio
curl http://localhost:5003/health
```

### Instalación Local (Desarrollo)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Configurar base de datos PostgreSQL
# Editar .env con credenciales de tu BD local

# 5. Inicializar base de datos
python init_db.py

# 6. Ejecutar servicio
python run.py
```

El servicio estará disponible en `http://localhost:5003`

## 🔍 API: Búsqueda de Productos (HU-22)

### Endpoint Principal

```http
GET /api/v1/inventory/search-product?q=<query>
```

**Requisito**: Tiempo de respuesta < 1 segundo

**Autenticación**: JWT Bearer Token requerido

**Parámetros**:
- `q` (required): Término de búsqueda (mínimo 2 caracteres)
  - Busca en: nombre del producto, código, referencia
  - Búsqueda case-insensitive
  - Soporta coincidencias parciales

### Ejemplos de Uso

```bash
# Buscar por nombre de producto
curl "http://localhost:5003/api/v1/inventory/search-product?q=Paracetamol" \
  -H "Authorization: Bearer <token>"

# Buscar por código de producto
curl "http://localhost:5003/api/v1/inventory/search-product?q=MED-001" \
  -H "Authorization: Bearer <token>"

# Buscar por referencia
curl "http://localhost:5003/api/v1/inventory/search-product?q=REF-PARA-500" \
  -H "Authorization: Bearer <token>"

# Búsqueda parcial (case-insensitive)
curl "http://localhost:5003/api/v1/inventory/search-product?q=parace" \
  -H "Authorization: Bearer <token>"
```

### Formato de Respuesta

```json
{
  "success": true,
  "message": "1 producto(s) encontrado(s)",
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "pasillo": "A",
      "estanteria": "01",
      "nivel": "1",
      "ubicacion": "Pasillo A - Estantería 01 - Nivel 1",
      "cantidad": 500.0,
      "status": "available",
      "created_at": "2024-10-26T10:30:00",
      "updated_at": "2024-10-26T10:30:00",
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

### Códigos de Respuesta

- `200 OK`: Búsqueda exitosa (con o sin resultados)
- `400 Bad Request`: Parámetro `q` faltante o muy corto (< 2 caracteres)
- `401 Unauthorized`: Token JWT no proporcionado o inválido
- `500 Internal Server Error`: Error del servidor

## 🧪 Testing

El servicio incluye una suite completa de tests con **11 tests comprehensivos** que cubren todos los casos de uso.

### Ejecutar Tests

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests sin verificación de coverage
pytest tests/test_search_product.py -v --no-cov

# Ejecutar tests con reporte de coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Suite de Tests

1. ✅ **test_search_without_query_parameter** - Valida error 400 sin parámetro `q`
2. ✅ **test_search_with_short_query** - Valida error 400 con query < 2 caracteres
3. ✅ **test_search_by_product_name** - Búsqueda por nombre de producto
4. ✅ **test_search_by_product_code** - Búsqueda por código
5. ✅ **test_search_by_product_reference** - Búsqueda por referencia
6. ✅ **test_search_case_insensitive** - Verifica búsqueda case-insensitive
7. ✅ **test_search_partial_match** - Verifica coincidencias parciales
8. ✅ **test_search_no_results** - Manejo de búsquedas sin resultados
9. ✅ **test_search_response_format** - Valida estructura exacta de respuesta JSON
10. ✅ **test_search_without_authentication** - Verifica autenticación requerida
11. ✅ **test_ubicacion_format** - Valida formato de campo `ubicacion`

**Resultado**: ✅ 11 tests pasados, 0 fallos

## 📚 API Endpoints (Versión Simplificada)

### Búsqueda de Productos

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/v1/inventory/search-product?q=<query>` | Buscar productos por nombre, código o referencia | Sí (JWT) |

### Movimientos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/inventory/movements` | Historial de movimientos |

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |

## 📦 Ejemplos de Uso

### 1. Crear Item de Inventario

```bash
curl -X POST http://localhost:5003/api/v1/inventory \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 5,
    "bodega_id": 1,
    "pasillo": "A",
    "estanteria": "2",
    "nivel": "3",
    "lote": "L-2024-001",
    "fecha_vencimiento": "2025-12-31",
    "cantidad": 100,
    "cantidad_minima": 10,
    "cantidad_maxima": 500,
    "status": "available"
  }'
```

### 2. Ajustar Stock (Entrada)

```bash
curl -X POST http://localhost:5003/api/v1/inventory/15/adjust \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "entrada",
    "cantidad": 50,
    "motivo": "Compra a proveedor",
    "documento_referencia": "OC-2024-001"
  }'
```

### 3. Reservar Stock para Orden

```bash
curl -X POST http://localhost:5003/api/v1/inventory/15/reserve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "cantidad": 20,
    "motivo": "Orden de venta",
    "documento_referencia": "ORD-2024-0123"
  }'
```

### 4. Actualizar Ubicación

```bash
curl -X PUT http://localhost:5003/api/v1/inventory/15/location \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pasillo": "B",
    "estanteria": "5",
    "nivel": "1"
  }'
```

### 5. Buscar Inventario

```bash
# Buscar por producto y bodega
curl "http://localhost:5003/api/v1/inventory/search?product_id=5&bodega_id=1" \
  -H "Authorization: Bearer <token>"

# Buscar items con stock bajo
curl "http://localhost:5003/api/v1/inventory/search?stock_bajo=true" \
  -H "Authorization: Bearer <token>"

# Buscar por ubicación
curl "http://localhost:5003/api/v1/inventory/search?pasillo=A&estanteria=2" \
  -H "Authorization: Bearer <token>"

# NUEVO: Buscar por nombre, código o referencia del producto
curl "http://localhost:5003/api/v1/inventory/search-product?q=paracetamol" \
  -H "Authorization: Bearer <token>"

# Buscar por código de producto
curl "http://localhost:5003/api/v1/inventory/search-product?q=MED-001" \
  -H "Authorization: Bearer <token>"

# Buscar y filtrar por bodega
curl "http://localhost:5003/api/v1/inventory/search-product?q=ibuprofeno&bodega_id=1" \
  -H "Authorization: Bearer <token>"
```

**Respuesta de búsqueda por producto:**

```json
{
  "success": true,
  "message": "2 producto(s) encontrado(s) en inventario",
  "data": [
    {
      "id": 15,
      "product_id": 5,
      "bodega_id": 1,
      "bodega_nombre": "Bodega Principal",
      "pasillo": "A",
      "estanteria": "2",
      "nivel": "3",
      "ubicacion_completa": "Bodega Principal - Pasillo A - Estantería 2 - Nivel 3",
      "lote": "L-2024-001",
      "fecha_vencimiento": "2025-12-31",
      "cantidad": "100.00",
      "cantidad_reservada": "20.00",
      "cantidad_disponible": "80.00",
      "status": "available",
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

### 6. Obtener Alertas

```bash
# Stock bajo en bodega 1
curl "http://localhost:5003/api/v1/inventory/alerts/low-stock?bodega_id=1" \
  -H "Authorization: Bearer <token>"

# Productos por vencer en 30 días
curl "http://localhost:5003/api/v1/inventory/alerts/expiring?dias=30" \
  -H "Authorization: Bearer <token>"
```

### 7. Consultar Movimientos

```bash
# Movimientos de un producto
curl "http://localhost:5003/api/v1/inventory/movements?product_id=5" \
  -H "Authorization: Bearer <token>"

# Movimientos por tipo
curl "http://localhost:5003/api/v1/inventory/movements?tipo=entrada" \
  -H "Authorization: Bearer <token>"

# Movimientos en rango de fechas
curl "http://localhost:5003/api/v1/inventory/movements?fecha_desde=2024-01-01&fecha_hasta=2024-12-31" \
  -H "Authorization: Bearer <token>"
```

## 🔐 Autenticación

Todas las rutas (excepto `/health`) requieren autenticación JWT:

```bash
Authorization: Bearer <token>
```

El token se obtiene del servicio de autenticación:

```bash
# Login
curl -X POST http://localhost:9001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 🏗️ Arquitectura

### Modelo de Datos

**NOTA IMPORTANTE**: Este servicio comparte la base de datos con `products-service`, permitiendo realizar JOINs eficientes sin llamadas HTTP entre microservicios. El modelo `Product` es de solo lectura (READ-ONLY) en este servicio.

#### Tabla: inventory_items

| Campo | Tipo | Descripción | Índice |
|-------|------|-------------|--------|
| id | Integer | ID único | PK |
| **product_id** | Integer | **Referencia a products-service** | FK, Índice |
| **bodega_id** | Integer | ID de bodega | Índice |
| bodega_nombre | String(100) | Nombre de bodega | No |
| **pasillo** | String(20) | Ubicación: Pasillo | Índice |
| **estanteria** | String(20) | Ubicación: Estantería | Índice |
| **nivel** | String(20) | Ubicación: Nivel | Índice |
| **lote** | String(50) | Número de lote | Índice |
| fecha_vencimiento | Date | Fecha de vencimiento | Índice |
| cantidad | Numeric(10,2) | Stock total | No |
| cantidad_reservada | Numeric(10,2) | Stock reservado | No |
| cantidad_disponible | Numeric(10,2) | Stock disponible | No |
| cantidad_minima | Numeric(10,2) | Stock mínimo (alerta) | No |
| cantidad_maxima | Numeric(10,2) | Stock máximo (alerta) | No |
| status | String(20) | Estado del inventario | No |
| costo_almacenamiento | Numeric(10,2) | Costo de almacenamiento | No |
| created_at | DateTime | Fecha de creación | No |
| updated_at | DateTime | Última actualización | No |

**Estados (InventoryStatus)**:
- `available`: Disponible
- `reserved`: Reservado
- `quarantine`: En cuarentena
- `damaged`: Dañado
- `expired`: Vencido
- `in_transit`: En tránsito

**Índices para Performance**:
- `idx_product_bodega`: (product_id, bodega_id) - Búsqueda rápida
- `idx_location`: (pasillo, estanteria, nivel) - Búsqueda por ubicación
- `idx_product_lote`: (product_id, lote) - Búsqueda por lote
- `idx_vencimiento`: (fecha_vencimiento) - Alertas de vencimiento
- `idx_stock_bajo`: WHERE cantidad <= cantidad_minima

#### Tabla: inventory_movements

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | ID único |
| inventory_item_id | Integer | FK a inventory_items |
| product_id | Integer | Referencia a producto |
| bodega_id | Integer | Bodega del movimiento |
| **tipo** | String(20) | Tipo de movimiento |
| cantidad | Numeric(10,2) | Cantidad movida |
| cantidad_anterior | Numeric(10,2) | Stock antes del movimiento |
| cantidad_nueva | Numeric(10,2) | Stock después del movimiento |
| motivo | Text | Razón del movimiento |
| documento_referencia | String(50) | OC, factura, orden, etc. |
| usuario_id | Integer | Usuario que realizó el movimiento |
| usuario_nombre | String(100) | Nombre del usuario |
| lote | String(50) | Lote afectado |
| fecha_movimiento | DateTime | Fecha/hora del movimiento |

**Tipos de Movimiento (MovementType)**:
- `entrada`: Ingreso de mercancía
- `salida`: Salida de mercancía
- `ajuste`: Ajuste de inventario
- `transferencia`: Transferencia entre bodegas
- `devolucion_cliente`: Devolución de cliente
- `devolucion_proveedor`: Devolución a proveedor
- `merma`: Pérdida o deterioro

## ⚙️ Configuración

### Variables de Entorno

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Servidor
PORT=5003
HOST=0.0.0.0

# Base de Datos
DATABASE_URL=postgresql://inventory_user:inventory_pass@localhost:5434/inventory_db

# Auth Service
AUTH_SERVICE_URL=http://localhost:9001

# Products Service (para integración futura)
PRODUCTS_SERVICE_URL=http://localhost:5002

# Performance (HU-22)
SEARCH_TIMEOUT=1.0              # Timeout de búsqueda en segundos
MAX_RESULTS_PER_PAGE=100
DEFAULT_PAGE_SIZE=20

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/inventory-service.log
```

## 🧪 Testing

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_inventory.py
pytest tests/test_movements.py
pytest tests/test_search_performance.py
```

## 📊 Integración con Otros Servicios

### products-service

Este servicio referencia productos por `product_id`. Para obtener información del producto:

```bash
# En inventory-service obtenemos el product_id
GET /api/v1/inventory/15
# Response: {"product_id": 5, "cantidad": 100, ...}

# Luego consultamos products-service
GET http://localhost:5002/api/v1/products/5
# Response: {"nombre": "Paracetamol 500mg", "codigo": "MED-001", ...}
```

### orders-service

Reservas de stock para órdenes:

1. orders-service crea una orden
2. orders-service solicita reserva a inventory-service:
   ```bash
   POST /api/v1/inventory/15/reserve
   ```
3. inventory-service reduce `cantidad_disponible` y aumenta `cantidad_reservada`
4. Se crea un movimiento de tipo `reserva`

### Flujo de Integración

```
┌─────────────────┐    product_id    ┌──────────────────┐
│ products-service│◄──────ref────────│inventory-service │
└─────────────────┘                  └──────────────────┘
                                              ▲
                                              │ reserve_stock
                                              │
                                     ┌────────┴────────┐
                                     │ orders-service  │
                                     └─────────────────┘
```

## 🚀 Despliegue

### Docker Compose

```bash
docker-compose up -d --build
docker-compose logs -f inventory-service
```

### Kubernetes

Consultar `deploy-medisupply/k8s/` para manifiestos.

## 📈 Performance

### Optimizaciones

- ✅ Índices compuestos en (product_id, bodega_id)
- ✅ Índices en ubicación (pasillo, estanteria, nivel)
- ✅ Índices parciales para alertas
- ✅ Connection pooling
- ✅ Query optimization con SQLAlchemy

### Benchmarks

- Localización de producto: ~0.15s
- Búsqueda con filtros: ~0.25s
- Ajuste de stock: ~0.10s

## 🔗 Servicios Relacionados

- **auth-service**: http://localhost:9001 - Autenticación
- **products-service**: http://localhost:5002 - Catálogo de productos
- **crm-service**: http://localhost:5001 - Clientes
- **orders-service**: http://localhost:5004 - Órdenes
- **managers-service**: http://localhost:5005 - Gerentes

---

**Desarrollado para MediSupply Backend Microservices**
