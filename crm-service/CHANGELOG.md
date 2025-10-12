# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2025-10-12

### Añadido
- ✨ Implementación inicial del servicio CRM
- ✨ Módulo de proveedores (Suppliers)
  - Registro de proveedores con todos los campos requeridos
  - Validación de NIT único
  - Carga de certificados con validación de formato
  - Búsqueda y filtrado de proveedores
  - Paginación de resultados
  - Soft delete (eliminación lógica)
- ✨ Sistema de autenticación con JWT
- ✨ Middleware de logging de requests
- ✨ Manejo global de errores
- ✨ Sistema de auditoría completo (creado por, fecha/hora, modificado por, eliminado por)
- ✨ Validaciones robustas:
  - Formato de NIT
  - Formato de teléfono
  - Formato de email
  - Tipo y tamaño de archivos
  - Validación de tipo MIME
- ✨ Documentación completa de API
- ✨ Tests unitarios básicos
- ✨ Configuración de Docker y Docker Compose
- ✨ Scripts de inicialización
- ✨ Arquitectura modular limpia

### Seguridad
- 🔒 Autenticación requerida en todos los endpoints
- 🔒 Validación de tipos MIME para prevenir archivos maliciosos
- 🔒 Nombres de archivo seguros
- 🔒 Protección contra inyección SQL (uso de ORM)
- 🔒 Variables de entorno para datos sensibles

### Documentación
- 📝 README completo
- 📝 Documentación de API
- 📝 Ejemplos de uso
- 📝 Guía de instalación
- 📝 Estructura del proyecto documentada

## [Unreleased]

### Planeado
- Módulo de vendedores (Sellers)
- Módulo de clientes (Clients)
- Módulo de productos (Products)
- Dashboard de estadísticas
- Exportación de reportes
- Notificaciones por email
- API de integración con otros servicios
