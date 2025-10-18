# Managers Service

Microservicio mínimo para gestionar Gerentes de Cuenta (Account Managers).

Endpoints principales:
- POST /api/v1/managers -> Crear gerente
- GET /api/v1/managers -> Listar gerentes
- POST /api/v1/managers/<manager_id>/assign -> Asignar cliente a gerente
- POST /api/v1/clients -> Crear cliente (test/setup)
- GET /api/v1/clients/<client_id>/manager -> Obtener gerente activo del cliente

Uso en pruebas: sqlite en memoria.
