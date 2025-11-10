# Visits API (Planificación y registro de visitas)

Microservicio para **planear rutas** y **registrar visitas** con secuencia planificada (1..N) según el orden de clientes. Sigue el patrón `controllers / services / repositories / domain / util / tests` (igual a *video-api*).

---

## Endpoints
- `GET /health` — Verifica estado del servicio.
- `POST /visits` — Crear agenda/visita del día (idVisita, id comercial, lista de idClientes, fecha).
- `GET /visits` — Listar todas las visitas (paginación por `limit` y `cursor`).
- `GET /visits/by-dates?from=ISO&to=ISO` — Listar visitas por rango de fechas.
- `GET /visits/by-commercial/<commercial_id>` — Listar visitas por id del comercial.

> La secuencia planificada se define por la posición en el arreglo `client_ids`. El backend guarda `stops[position=1..N]`.

### Estados/resultado (pensados para futuras extensiones)
- `VisitStatus`: `planned | in_progress | finished | rescheduled`
- `VisitResult`: `success | rescheduled | failed`

---

## Auth
Validación opcional (se puede enviar):
```
Authorization: Bearer <token>
```
> En local no es obligatorio; puedes endurecerlo después.

---

## Base de datos
- **Prod/Dev por defecto**: PostgreSQL como en *video-api*  
  `DATABASE_URL=postgresql+psycopg2://app:app@medisupply-db:5432/medisupplydb`
- **Pruebas**: el fixture usa SQLite aislado (no excluido del ZIP).

---

## Correr local
```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://app:app@medisupply-db:5432/medisupplydb"
python -m app.app
# Servicio en: http://localhost:9022
```

## Pruebas (≥90% cobertura)
```bash
pytest -q --cov=app --cov-report=term-missing
```

## Docker
```bash
docker build -t visits-api:local .
docker run --rm -p 9022:9022   -e DATABASE_URL="postgresql+psycopg2://app:app@medisupply-db:5432/medisupplydb"   visits-api:local
```

---

## Esquema de datos
**Tabla `visits`**
- `id` *(idVisita)*, `commercial_id`, `date` (ISO), `created_at`
**Tabla `visit_stops`**
- `id`, `visit_id`, `client_id`, `position` *(1..N)*, `status`, `checkin_at`, `checkout_at`, `lat`, `lon`, `duration_minutes`, `result`, `result_reason`, `notes`, `tags`

---

## cURL de referencia

### 1) Health
```bash
curl -s "http://localhost:9022/health" | jq .
```

### 2) Crear visita / agenda (POST /visits)
```bash
curl -s -X POST "http://localhost:9022/visits"   -H "Content-Type: application/json"   -d '{
        "visit_id": 1001,
        "commercial_id": 7,
        "date": "2025-10-25T09:00:00",
        "client_ids": [10, 20, 30]
      }' | jq .
```
**Respuesta 201 ejemplo**
```json
{
  "id": 1001,
  "commercial_id": 7,
  "date": "2025-10-25T09:00:00Z",
  "stops": [
    {"client_id": 10, "position": 1, "status": "planned"},
    {"client_id": 20, "position": 2, "status": "planned"},
    {"client_id": 30, "position": 3, "status": "planned"}
  ]
}
```
**Errores**
- `400 {"error":"missing_fields"}` (faltan campos)
- `400 {"error":"invalid_date"}` (fecha inválida)
- `400 {"error":"invalid_clients"}` (lista vacía/no array)

### 3) Listar todas (GET /visits)
```bash
# Primera página (10)
curl -s "http://localhost:9022/visits?limit=10" | jq .

# Siguiente (usa el next_cursor que te devolvió la anterior)
curl -s "http://localhost:9022/visits?limit=10&cursor=LAST_ID" | jq .
```

**Respuesta ejemplo**
```json
{
  "items": [
    {
      "id": 1001,
      "commercial_id": 7,
      "date": "2025-10-25T09:00:00Z",
      "stops": [
        {"client_id": 10, "position": 1, "status": "planned"},
        {"client_id": 20, "position": 2, "status": "planned"},
        {"client_id": 30, "position": 3, "status": "planned"}
      ]
    }
  ],
  "next_cursor": null
}
```

### 4) Por fechas (GET /visits/by-dates)
```bash
curl -s "http://localhost:9022/visits/by-dates?from=2025-10-20T00:00:00&to=2025-10-30T23:59:59" | jq .
```

### 5) Por comercial (GET /visits/by-commercial/<id>)
```bash
curl -s "http://localhost:9022/visits/by-commercial/7?limit=20" | jq .
```

---

## Estructura del proyecto
```
app/
  app.py
  db.py
  controllers/visits_controller.py
  services/visits_service.py
  repositories/visits_repository.py
  domain/visit.py
  util/auth_mw.py
tests/
  conftest.py
  test_visits_api.py
Dockerfile
requirements.txt
Makefile
service.json
README.md
```
