# Python Microservices — Auth + (New Micro) (Flask)

## Servicios
- **auth-service** (puerto 9001): `/auth/login`, `/auth/verify` — emite y valida JWT (HS256) con claim `role`.
- **Api de ejemplo, compiar por cada micro** **resource-api** (puerto 9002): `/whoami` (requiere token) y `/admin/sensitive-op` (requiere `role=security_admin`).

## Ejecutar local con Docker
```bash
cd py-ms-auth
docker compose up --build -d
```

## Probar con curl
```bash
# login admin
TOKEN=$(curl -s -X POST http://localhost:9001/auth/login -H "Content-Type: application/json" -d '{"email":"admin@medisupply.com","password":"Admin#123"}' | jq -r .access_token)

# ver identidad
curl -H "Authorization: Bearer $TOKEN" http://localhost:9002/whoami

# operación admin
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:9002/admin/sensitive-op
```

## Configuración
- `JWT_SECRET` (compartido por ambos servicios).
- `USERS_JSON` (solo auth-service): lista de usuarios con `email`, `password`, `role`.
- `ALLOWED_ORIGINS` para CORS en resource-api.

## Inventory-service: Productos de ejemplo

El `inventory-service` incluye un seeder de desarrollo que crea una tabla `products` simple
(solo si no existe) y carga una lista de productos de ejemplo cuando la variable de entorno
`INIT_DB` está establecida a `true` al arrancar el contenedor. Esto se usa para pruebas locales
y demostraciones.

Lista de productos que el seeder crea (id incrementales):

1. Paracetamol 500mg — MED-001
2. Ibuprofeno 400mg — MED-002
3. Amoxicilina 500mg — MED-003
4. Omeprazol 20mg — MED-004
5. Losartán 50mg — MED-005
6. Metformina 850mg — MED-006
7. Simvastatina 20mg — MED-007
8. Aspirina 100mg — MED-008
9. Cetirizina 10mg — MED-009

Notas importantes:
- El seeder está pensado para entornos de desarrollo/local. En producción normalmente los
	productos deben ser creados y gestionados por el `products-service` (o por tu pipeline).
- Para evitar inserciones accidentales en producción, no definas `INIT_DB=true` en tu
	configuración de despliegue en la nube, o usa la variable adicional `ALLOW_INIT_DB_IN_PROD`
	para permitirlo explícitamente. Podemos añadir esta comprobación al `entrypoint.sh` si lo
	quieres (recomendado).

