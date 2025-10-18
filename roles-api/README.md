# Roles API (JST + User + Roles)

## Endpoints
- `GET /api/users-with-roles`
- `PUT /api/users/{uid}/roles-permissions`
- `GET/POST /api/users`
- `GET/POST /api/roles`

## Auth
Validación **local** del JWT (HS256) con `JWT_SECRET`. Coincide con `auth-service`.

## Correr local
```bash
pip install -r requirements.txt
export JWT_SECRET=supersecret
python -m flask --app app.app:app run -p 9003
```

## Pruebas (solo pytest)
```bash
pytest -q
```

## Docker (solo roles-api)
```bash
docker compose up --build -d
```

## Pruebas CURL
```bash
#Token
TOKEN=$(curl -s -X POST http://localhost:9001/auth/login -H "Content-Type: application/json" -d '{"email":"admin@medisupply.com","password":"Admin#123"}' | jq -r .access_token)

#Consulta usuarios con sus roles
curl -s "http://localhost:9003/api/users-with-roles" \
  -H "Authorization: Bearer $TOKEN"

#Consulta usuarios
curl -s "http://localhost:9003/api/users" \
  -H "Authorization: Bearer $TOKEN"

#Crea usuario
curl -s -X POST "http://localhost:9001/api/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"names":"Nuevo Usuario","email":"nuevo@acme.com","password":"Secreta#123"}'

#Consulta Roles
curl -s "http://localhost:9003/api/roles" \
  -H "Authorization: Bearer $TOKEN"

#Asigna permisos a usuario
UID=1 #id de usuario
ROLE_ID=1   # por ejemplo, el id del rol "Compras"

curl -s -X PUT "http://localhost:9003/api/users/$UID/roles-permissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "assignments": [
          {
            "role_id": "$ROLE_ID", "can_create": false, "can_edit": false, "can_delete": false, "can_view": true 
            }
        ]
      }'
```
```bash
# Prueba el end point de control de acceso
curl -X POST "http://localhost:9003/api/access-control" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
        "email": "juan@example.com",
        "rol": "Admin",
        "action": "create"
      }'
      
```

