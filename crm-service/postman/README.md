# CRM Service - Postman Collection

Esta carpeta contiene las colecciones de Postman para probar la API del servicio CRM.

## Configuración

1. Importa la colección en Postman
2. Configura las variables de entorno:
   - `base_url`: URL base del servicio (ej: http://localhost:5002)
   - `auth_token`: Token JWT para autenticación

## Endpoints Disponibles

### Suppliers (Proveedores)

- **POST** `/api/v1/suppliers` - Crear proveedor
- **GET** `/api/v1/suppliers` - Listar proveedores
- **GET** `/api/v1/suppliers/:id` - Obtener proveedor
- **PUT** `/api/v1/suppliers/:id` - Actualizar proveedor
- **DELETE** `/api/v1/suppliers/:id` - Eliminar proveedor
- **GET** `/api/v1/suppliers/stats` - Estadísticas

## Ejemplo de Request

```json
POST /api/v1/suppliers
Headers:
  Authorization: Bearer {{auth_token}}
  
Body (form-data):
  razon_social: Empresa Ejemplo SA
  nit: 123456789-0
  representante_legal: Juan Pérez
  pais: Colombia
  nombre_contacto: María García
  celular_contacto: 3001234567
  certificado: [archivo]
```
