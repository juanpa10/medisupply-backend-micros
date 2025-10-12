# CRM Service - MediSupply

Servicio de gestión de relaciones con clientes (CRM) para el sistema MediSupply.

## 🎯 Historia de Usuario - HU-32

**Como** Gerente de cuenta  
**Quiero** registrar proveedores con información completa y validada  
**Para** comparar fabricantes y mejorar las opciones de negociación regional

## ✨ Características

- **Gestión de Proveedores**: Registro completo de proveedores con validación de datos
- **Validaciones Robustas**: Validación de NIT único, formatos de archivo, tipos MIME
- **Auditoría Completa**: Trazabilidad de todas las operaciones (usuario, fecha, hora)
- **Seguridad**: Autenticación JWT, validación de archivos, protección contra malware
- **API REST**: Endpoints completos para CRUD de proveedores con paginación y filtros

## Estructura del Proyecto

```
crm-service/
├── app/
│   ├── config/          # Configuración
│   ├── core/            # Funcionalidad central
│   ├── shared/          # Código compartido
│   └── modules/         # Módulos de negocio
├── uploads/             # Archivos subidos
├── logs/                # Logs de la aplicación
└── run.py              # Punto de entrada
```

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (opcional)

## Instalación Local

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar migraciones:
```bash
flask db upgrade
```

5. Ejecutar aplicación:
```bash
python run.py
```

## Instalación con Docker

```bash
docker-compose up -d
```

## 📡 API Endpoints

### Proveedores
- `POST /api/v1/suppliers` - Registrar proveedor
- `GET /api/v1/suppliers` - Listar proveedores (paginado, con filtros)
- `GET /api/v1/suppliers/stats` - Estadísticas de proveedores
- `GET /api/v1/suppliers/{id}` - Obtener proveedor específico
- `PUT /api/v1/suppliers/{id}` - Actualizar proveedor
- `DELETE /api/v1/suppliers/{id}` - Eliminar proveedor (soft delete)

### Health Check
- `GET /health` - Estado del servicio

## 🧪 Pruebas

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html
```

## 📚 Documentación Adicional

- [API_DOCS.md](API_DOCS.md) - Documentación completa de la API
- [CHANGELOG.md](CHANGELOG.md) - Registro de cambios

## 📝 Licencia

Propietario - MediSupply © 2025
