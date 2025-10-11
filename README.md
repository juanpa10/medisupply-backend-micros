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
