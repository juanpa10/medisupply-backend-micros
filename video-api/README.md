
# Video API (Evidencia visual)

## Endpoints
- `POST /evidence/upload` — Carga de imagen o video (multipart/form-data)
- `GET /evidence/<id>` — Obtiene metadatos y URL firmada temporal
- `GET /evidence` — Lista evidencias recientes
- `GET /files?path=...&exp=...&sig=...` — Descarga protegida con firma HMAC
- `GET /health` — Verifica estado del servicio

## Auth
Validación **opcional** del JWT (HS256) con `SECRET_KEY`.  
Por ahora no bloquea si no se envía token, pero acepta encabezado:
`Authorization: Bearer <token>`

## Correr local
```bash
pip install -r requirements.txt
export SECRET_KEY=supersecret
export UPLOAD_DIR=./data/uploads
python -m flask --app app.app:app run -p 9005
```

## Pruebas (solo pytest)
```bash
pytest -q
# Cobertura (objetivo 90%)
pytest -q --cov=app --cov-report=term-missing
```

## Docker (solo video-api)
```bash
docker build -t pyms-video-api:local .
docker run --rm -p 9005:9005   -e SECRET_KEY=supersecret   -e UPLOAD_DIR=/srv/app/data/uploads   -v $PWD/data/uploads:/srv/app/data/uploads   pyms-video-api:local
```

## Pruebas CURL

### Obtener token (opcional, si está corriendo auth-service)
```bash
TOKEN=$(curl -s -X POST http://localhost:9001/auth/login   -H "Content-Type: application/json"   -d '{"email":"admin@medisupply.com","password":"Admin#123"}' | jq -r .access_token)
```

### Subir foto (válida, ≤10 MB)
```bash
curl -s -X POST "http://localhost:9020/evidence/upload"   -H "Authorization: Bearer $TOKEN"   -F "file=@/c/Users/andre/OneDrive/Imágenes/imagen.jpg"   -F "client_id=C1"   -F "product_id=P1"   -F "visit_id=V1"   -F "evidence_type=photo"  | jq .
```

### Subir video (válido, ≤200 MB)
```bash
curl -s -X POST "http://localhost:9020/evidence/upload"   -H "Authorization: Bearer $TOKEN"   -F "file=@/ruta/tu_video.mp4"   -F "client_id=C1"   -F "product_id=P1"   -F "visit_id=V1"   -F "evidence_type=video" | jq .
```

### Formato no soportado
```bash
curl -s -X POST "http://localhost:9020/evidence/upload"   -H "Authorization: Bearer $TOKEN"   -F "file=@/ruta/archivo.gif"   -F "client_id=C1"   -F "product_id=P1"   -F "visit_id=V1"   -F "evidence_type=photo" | jq .
# → {"error":"Formato de foto no soportado"}
```

### Archivo demasiado grande
```bash
curl -s -X POST "http://localhost:9020/evidence/upload"   -H "Authorization: Bearer $TOKEN"   -F "file=@/ruta/foto_grande.png"   -F "client_id=C1"   -F "product_id=P1"   -F "visit_id=V1"   -F "evidence_type=photo" | jq .
# → {"error":"Archivo demasiado grande (foto)"}
```

### Consulta de evidencia
```bash
curl -s "http://localhost:9020/evidence/$EVID_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .
```  

### Descargar usando URL firmada
```bash
SIGNED_URL=$(curl -s "http://localhost:9020/evidence/$EVID_ID"   -H "Authorization: Bearer $TOKEN" | jq -r .signed_url)
curl -s -L "http://localhost:9020$SIGNED_URL" -o evidencia.bin
file evidencia.bin
```

### Healthcheck
```bash
curl -s "http://localhost:9020/health" | jq .
```

