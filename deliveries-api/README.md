# Deliveries API (Entregas)

Microservicio para **gestionar entregas** asociadas a pedidos y clientes. Permite **crear** entregas, **listar todas** y **consultar por cliente**. Sigue el patrón `controllers / services / repositories / domain / util / tests` (igual a *video-api*).

---

## Endpoints
- `POST /deliveries` — Crear entrega  
- `GET /deliveries` — Listar entregas (paginación por `limit` y `cursor`)  
- `GET /deliveries/client/<client_id>` — Listar entregas por cliente  
- `GET /health` — Verifica estado del servicio

### Estados permitidos
`alistamiento`, `despachado`, `entregado`

---

## Auth
Validación opcional (header admitido):
```
Authorization: Bearer <token>
```
> El servicio funciona sin token en local; puedes endurecerlo luego.

---

## Correr local
```bash
# Requisitos
#  - Python 3.11+
#  - (Opcional) setear DATABASE_URL (por defecto usa SQLite ./deliveries.db)

pip install -r requirements.txt
export DATABASE_URL="sqlite:///./deliveries.db"   # o postgresql+psycopg2://user:pass@host:5432/db
python -m app.app
# Servicio en: http://localhost:9021
```

---

## Pruebas (objetivo ≥95% cobertura)
```bash
pytest -q --cov=app --cov-report=term-missing
```

---

## Docker
```bash
docker build -t deliveries-api:local .
docker run --rm -p 9021:9021   -e DATABASE_URL="sqlite:///./deliveries.db"   deliveries-api:local
```

---

## Esquema de datos (tabla `deliveries`)
- `id` (int, PK)
- `order_id` (int, requerido, index)
- `client_id` (int, requerido, index)
- `delivery_date` (datetime ISO, requerido) — ej. `2025-10-25T10:00:00`
- `status` (string, requerido) — uno de: `alistamiento|despachado|entregado`
- `created_at` (datetime, auto)
- `updated_at` (datetime, auto)

---

## Pruebas CURL

### 1) Healthcheck
```bash
curl -s "http://localhost:9021/health" | jq .
```

### 2) Crear entrega
```bash
curl -s -X POST "http://localhost:9021/deliveries"   -H "Content-Type: application/json"   -d '{
        "order_id": 11,
        "client_id": 99,
        "delivery_date": "2025-10-25T10:00:00",
        "status": "alistamiento"
      }' | jq .
```
**Respuesta (200/201) ejemplo**
```json
{
  "id": 1,
  "order_id": 11,
  "client_id": 99,
  "delivery_date": "2025-10-25T10:00:00Z",
  "status": "alistamiento"
}
```
**Errores**
- Campos faltantes → `400 {"error":"missing_fields"}`
- Estado inválido → `400 {"error":"invalid_status","allowed":["alistamiento","despachado","entregado"]}`
- Fecha inválida → `400 {"error":"invalid_date"}`

### 3) Listar TODAS las entregas (paginación por cursor)
```bash
# Primer page (hasta 10 resultados)
curl -s "http://localhost:9021/deliveries?limit=10" | jq .

# Siguiente page (usa el next_cursor anterior)
curl -s "http://localhost:9021/deliveries?limit=10&cursor=LAST_ID" | jq .
```
**Respuesta ejemplo**
```json
{
  "items": [
    {
      "id": 1,
      "order_id": 11,
      "client_id": 99,
      "delivery_date": "2025-10-25T10:00:00Z",
      "status": "alistamiento"
    }
  ],
  "next_cursor": null
}
```

### 4) Listar entregas por **cliente**
```bash
curl -s "http://localhost:9021/deliveries/client/99?limit=20" | jq .
```

