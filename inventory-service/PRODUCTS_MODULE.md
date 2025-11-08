# Módulo de Productos - Inventory Service

## 📋 Descripción

Este módulo implementa la **HU (Historia de Usuario)** de **registro de productos** como proveedor, permitiendo crear productos con su ficha técnica, condiciones de almacenamiento y certificaciones sanitarias para que estén disponibles en el catálogo de MediSupply.

## ✅ Criterios de Aceptación Implementados

- ✅ **El sistema permite crear un nuevo producto con nombre, descripción y categoría**
- ✅ **Se pueden cargar ficha técnica, condiciones de almacenamiento y certificaciones sanitarias**
- ✅ **Los documentos y datos cargados quedan asociados al producto**
- ✅ **El producto registrado aparece en el catálogo de MediSupply disponible para los clientes**
- ✅ **El sistema valida que los campos obligatorios estén completos antes de guardar**

## 🏗️ Arquitectura

### Modelos de Datos

#### `Product` - Modelo Principal
- **Información básica**: nombre, código, referencia, descripción
- **Categorización**: categoria_id, unidad_medida_id, proveedor_id (FK)
- **Precios**: precio_compra, precio_venta
- **Control de documentos**: flags para requerir cada tipo de documento
- **Estado**: active, inactive, discontinued

#### `ProductFile` - Gestión de Archivos
- **Categorías soportadas**:
  - `technical_sheet` - Ficha técnica
  - `storage_conditions` - Condiciones de almacenamiento  
  - `health_certifications` - Certificaciones sanitarias
- **Metadatos**: nombre original, almacenado, tipo MIME, tamaño, ruta
- **Auditoría**: usuario, fecha de subida

#### Modelos de Referencia
- **`Categoria`**: Categorías de productos
- **`UnidadMedida`**: Unidades de medida (tableta, cápsula, ml, etc.)
- **`Proveedor`**: Información de proveedores

### Capas de la Aplicación

```
routes.py (REST API) 
    ↓
controller.py (HTTP handlers)
    ↓  
service.py (Lógica de negocio)
    ↓
repository.py (Acceso a datos)
    ↓
models.py (SQLAlchemy ORM)
```

## 🚀 API Endpoints

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/products` | Crear producto con archivos |
| `GET` | `/api/v1/products` | Listar productos (paginado) |
| `GET` | `/api/v1/products/search` | Buscar productos con filtros |
| `GET` | `/api/v1/products/{id}` | Obtener producto específico |
| `PUT` | `/api/v1/products/{id}` | Actualizar producto |
| `DELETE` | `/api/v1/products/{id}` | Eliminar producto (soft delete) |

### Gestión de Archivos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/products/{id}/files` | Agregar archivo |
| `GET` | `/api/v1/products/{id}/files` | Listar archivos |
| `GET` | `/api/v1/products/files/{file_id}/download` | Descargar archivo |
| `DELETE` | `/api/v1/products/files/{file_id}` | Eliminar archivo |

### Estado del Catálogo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/products/{id}/catalog-status` | Estado del producto en catálogo |
| `GET` | `/api/v1/products/missing-documents` | Productos sin documentos |

### Datos Maestros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST/GET` | `/api/v1/categorias` | Gestionar categorías |
| `POST/GET` | `/api/v1/unidades-medida` | Gestionar unidades |
| `POST/GET` | `/api/v1/proveedores` | Gestionar proveedores |

## 📝 Ejemplos de Uso

### 1. Crear Producto (Como Proveedor)

```bash
# Crear producto con archivos usando multipart/form-data
curl -X POST http://localhost:9008/api/v1/products \
  -H "Authorization: Bearer <token>" \
  -F "nombre=Paracetamol 500mg" \
  -F "codigo=PARA-500" \
  -F "descripcion=Analgésico y antipirético para alivio del dolor" \
  -F "categoria_id=1" \
  -F "unidad_medida_id=1" \
  -F "proveedor_id=1" \
  -F "precio_venta=0.80" \
  -F "requiere_ficha_tecnica=true" \
  -F "requiere_condiciones_almacenamiento=true" \
  -F "requiere_certificaciones_sanitarias=true" \
  -F "technical_sheet=@ficha_tecnica.pdf" \
  -F "storage_conditions=@condiciones_almacenamiento.pdf" \
  -F "health_certifications=@certificaciones.pdf"
```

### 2. Buscar Productos en Catálogo

```bash
# Buscar productos disponibles
curl -X GET "http://localhost:9008/api/v1/products/search?q=paracetamol&status=active" \
  -H "Authorization: Bearer <token>"
```

### 3. Verificar Estado del Catálogo

```bash
# Verificar si producto está disponible en catálogo
curl -X GET http://localhost:9008/api/v1/products/1/catalog-status \
  -H "Authorization: Bearer <token>"

# Respuesta:
{
  "success": true,
  "data": {
    "product_id": 1,
    "catalog_status": "available",  # available | pending_documents | unavailable
    "message": "Disponible en catálogo",
    "has_required_documents": true,
    "required_documents": {
      "technical_sheet": true,
      "storage_conditions": true, 
      "health_certifications": true
    },
    "uploaded_documents": {
      "technical_sheet": true,
      "storage_conditions": true,
      "health_certifications": true
    }
  }
}
```

### 4. Productos Sin Documentos Completos

```bash
# Obtener productos que faltan documentos
curl -X GET http://localhost:9008/api/v1/products/missing-documents \
  -H "Authorization: Bearer <token>"
```

## 🗂️ Validaciones Implementadas

### Campos Obligatorios
- ✅ **nombre** (2-200 caracteres, alfanumérico)
- ✅ **codigo** (3-50 caracteres, único, mayúsculas/números/guiones)
- ✅ **descripcion** (10-1000 caracteres)
- ✅ **categoria_id** (FK válida)
- ✅ **unidad_medida_id** (FK válida)
- ✅ **proveedor_id** (FK válida)

### Validaciones de Archivos
- ✅ **Extensiones permitidas**: .pdf, .doc, .docx, .jpg, .jpeg, .png, .txt
- ✅ **Tamaño máximo**: 5MB por archivo
- ✅ **Categorías válidas**: technical_sheet, storage_conditions, health_certifications
- ✅ **Nombres únicos** para archivos almacenados (UUID)

### Validaciones de Negocio
- ✅ **Código único** por producto
- ✅ **Precio de venta >= precio de compra** (si ambos están presentes)
- ✅ **Referencias FK válidas** antes de crear/actualizar
- ✅ **Estado del catálogo** basado en documentos requeridos

## 🧪 Testing y Datos de Muestra

### Ejecutar Tests
```bash
# Tests básicos (sin pytest)
python test_products_module.py

# Con pytest (si está instalado)
pytest test_products_module.py -v
```

### Crear Datos de Muestra
```bash
# Crear categorías, unidades, proveedores y productos de ejemplo
python create_products_sample_data.py
```

**Datos de muestra incluidos:**
- 7 categorías (Medicamentos, Antibióticos, Cardiovascular, etc.)
- 8 unidades de medida (Tableta, Cápsula, ML, etc.)
- 5 proveedores (Nacionales e internacionales)
- 6 productos de ejemplo (Paracetamol, Amoxicilina, etc.)

## 📂 Estructura de Archivos

```
app/modules/products/
├── __init__.py
├── models.py           # Product, ProductFile, Categoria, UnidadMedida, Proveedor
├── schemas.py          # Validaciones Marshmallow
├── repository.py       # Acceso a datos
├── service.py          # Lógica de negocio
├── controller.py       # Controladores REST
└── routes.py           # Blueprint y rutas

# Scripts de utilidad
├── create_products_sample_data.py
└── test_products_module.py
```

## 🔄 Estados del Producto en Catálogo

| Estado | Descripción | Criterios |
|--------|-------------|-----------|
| `available` | Disponible en catálogo | Status=active + documentos completos |
| `pending_documents` | Pendiente de documentos | Status=active + faltan documentos |
| `unavailable` | No disponible | Status!=active |

## 🔐 Seguridad y Autenticación

- ✅ **Autenticación requerida** en todos los endpoints (`@require_auth`)
- ✅ **Validación de archivos** (tipo, tamaño, extensión)
- ✅ **Nombres únicos** para archivos (previene colisiones)
- ✅ **Auditoría completa** (created_by, updated_by, timestamps)
- ✅ **Soft delete** (preserva historial)

## 🚀 Despliegue

### Variables de Entorno
```bash
# Configuración de archivos
UPLOAD_FOLDER=uploads/products
MAX_CONTENT_LENGTH=5242880  # 5MB en bytes

# Base de datos (compartida con inventory)
DATABASE_URL=postgresql://user:pass@localhost/inventory_db

# Autenticación
JWT_SECRET=your-secret-key
AUTH_SERVICE_URL=http://localhost:9001
```

### Docker
El módulo se integra automáticamente en el `inventory-service` existente. No requiere contenedor separado.

## 📈 Monitoreo

### Logs
- ✅ **Creación de productos** con detalles
- ✅ **Subida de archivos** con metadatos
- ✅ **Errores de validación** detallados
- ✅ **Estado del catálogo** por producto

### Métricas Disponibles
- Productos creados por día/mes
- Productos por estado de catálogo
- Documentos subidos por categoría
- Errores de validación más frecuentes

## 🎯 Próximas Mejoras

1. **Versioning de archivos** (mantener historial de documentos)
2. **Workflow de aprobación** (productos requieren aprobación)
3. **Notificaciones** (alertas de documentos vencidos)
4. **Búsqueda avanzada** (filtros por múltiples criterios)
5. **API de reportes** (analytics de catálogo)

---

## 👥 Como Proveedor - Flujo Completo

1. **Registrar información básica** del producto
2. **Subir documentos requeridos** (ficha técnica, condiciones, certificaciones)
3. **Sistema valida campos obligatorios** antes de guardar
4. **Producto aparece en catálogo** una vez completado
5. **Clientes pueden encontrar y solicitar** el producto

**¡El producto está ahora disponible en el catálogo de MediSupply!** 🎉