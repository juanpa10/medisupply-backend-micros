# Flask Auth Service (JWT + Roles)

Servicio de autenticación en **Flask** que emite y valida **JWT (HS256)** con claim `role`.

## Endpoints
- `GET /health` — estado.
- `POST /auth/login` — body: `{ "user": "...", "password": "..." }` → devuelve `{ access_token, role, expires_in }`.
- `GET /auth/verify` — `?token=...` o header `Authorization: Bearer <token>` → `{ valid, sub, role }`.

## Ejecutar con Docker
```bash
docker compose up --build -d
```

Variables de entorno:
- `JWT_SECRET` (por defecto `supersecret`).
- `ACCESS_TOKEN_EXPIRE_MINUTES` (por defecto 60).
- `USERS_JSON` — lista de usuarios en JSON. Ejemplo:
  ```json
  [{"user":"admin","password":"Admin#123","role":"security_admin"},
   {"user":"viewer","password":"Viewer#123","role":"viewer"}]
  ```

## Ejemplos (curl)
```bash
# Login (admin)
curl -s -X POST http://localhost:9001/auth/login  -H "Content-Type: application/json"  -d '{"user":"admin","password":"Admin#123"}'

# Verificar token (con header)
TOKEN=<pega_el_token>
curl -H "Authorization: Bearer $TOKEN" http://localhost:9001/auth/verify
```
