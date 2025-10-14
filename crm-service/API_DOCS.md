# Servicio CRM - Registro de Proveedores

## Descripción

Servicio para gestión de proveedores dentro del sistema MediSupply. Permite registrar proveedores con información completa y validada para comparar fabricantes y mejorar las opciones de negociación regional.

## Características Implementadas

### ✅ Registro de Proveedores
- Campos obligatorios:
  - Razón social
  - NIT (único en el sistema)
  - Representante legal
  - País
  - Nombre del contacto
  - Celular de contacto
  - Certificado (archivo adjunto)

### ✅ Validaciones
- Validación de todos los campos obligatorios
- Validación de formato de NIT
- Validación de formato de teléfono
- Validación de archivos (formatos permitidos: PDF, JPG, JPEG, PNG, TXT)
- Validación de tamaño máximo de archivo (5MB)
- Validación de tipo MIME para evitar archivos maliciosos
- Validación de NIT duplicado

### ✅ Auditoría
- Registro de usuario que crea/modifica/elimina
- Registro de fecha y hora de cada operación
- Soft delete (los registros no se eliminan físicamente)

### ✅ Seguridad
- Autenticación mediante JWT
- Validación de tipos MIME de archivos
- Nombres de archivo seguros
- Solo usuarios autenticados pueden acceder

### ✅ API REST
- `POST /api/v1/suppliers` - Registrar proveedor
- `GET /api/v1/suppliers` - Listar proveedores (con paginación y filtros)
- `GET /api/v1/suppliers/{id}` - Obtener proveedor específico
- `PUT /api/v1/suppliers/{id}` - Actualizar proveedor
- `DELETE /api/v1/suppliers/{id}` - Eliminar proveedor (soft delete)
- `GET /api/v1/suppliers/stats` - Estadísticas de proveedores

## Estructura del Proyecto

```
crm-service/
├── app/
│   ├── config/              # Configuración
│   │   ├── settings.py      # Variables de entorno
│   │   └── database.py      # Configuración de BD
│   ├── core/                # Funcionalidad central
│   │   ├── auth/            # Autenticación y autorización
│   │   ├── middleware/      # Middleware (errores, logging)
│   │   └── utils/           # Utilidades (validadores, respuestas)
│   ├── shared/              # Código compartido
│   │   ├── base_model.py    # Modelo base con auditoría
│   │   ├── base_repository.py # Repositorio base CRUD
│   │   └── enums.py         # Enumeraciones
│   └── modules/
│       └── suppliers/       # Módulo de proveedores
│           ├── models.py    # Modelo SQLAlchemy
│           ├── schemas.py   # Esquemas de validación
│           ├── repository.py # Acceso a datos
│           ├── service.py   # Lógica de negocio
│           ├── controller.py # Controladores
│           └── routes.py    # Rutas/Blueprint
├── tests/                   # Tests unitarios
├── uploads/                 # Archivos subidos
├── logs/                    # Logs de la aplicación
├── run.py                   # Punto de entrada
└── docker-compose.yml       # Configuración Docker
```

## Instalación

### Requisitos
- Python 3.11+
- PostgreSQL 15+

### Pasos

1. **Clonar el repositorio**
```bash
cd crm-service
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Crear base de datos**
```bash
# En PostgreSQL
CREATE DATABASE crm_db;
```

6. **Ejecutar migraciones**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. **Ejecutar aplicación**
```bash
python run.py
```

## Uso con Docker

```bash
# Construir y levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f crm-service

# Detener servicios
docker-compose down
```

## Uso de la API

### Registrar un Proveedor

```bash
curl -X POST http://localhost:5002/api/v1/suppliers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "razon_social=Empresa Ejemplo SA" \
  -F "nit=123456789-0" \
  -F "representante_legal=Juan Pérez" \
  -F "pais=Colombia" \
  -F "nombre_contacto=María García" \
  -F "celular_contacto=3001234567" \
  -F "certificado=@/path/to/certificate.pdf"
```

### Listar Proveedores

```bash
curl -X GET "http://localhost:5002/api/v1/suppliers?page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Filtrar Proveedores

```bash
# Por país
curl -X GET "http://localhost:5002/api/v1/suppliers?pais=Colombia" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Búsqueda por razón social o NIT
curl -X GET "http://localhost:5002/api/v1/suppliers?search=Empresa" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Tests

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

## Criterios de Aceptación ✅

- ✅ El sistema permite registrar todos los datos clave del proveedor
- ✅ Todos los campos del formulario son obligatorios
- ✅ El sistema muestra confirmación visual al registrar exitosamente
- ✅ La información queda almacenada en la tabla de proveedores
- ✅ Los movimientos guardan traza con usuario, fecha y hora
- ✅ En caso de error, se muestra mensaje de validación claro
- ✅ Validación de formatos de archivo permitidos
- ✅ Rechazo de NIT duplicado
- ✅ Solo usuarios autenticados pueden registrar proveedores
- ✅ El resumen de proveedores se actualiza en tiempo real

## Licencia

Propietario - MediSupply © 2025
