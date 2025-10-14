# 🚀 INICIO RÁPIDO - CRM Service

## Opción 1: Instalación Local (Desarrollo)

### Prerequisitos
- Python 3.11+
- PostgreSQL 15+
- Git

### Pasos

```bash
# 1. Navegar al directorio
cd crm-service

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones (especialmente DATABASE_URL)

# 6. Crear base de datos PostgreSQL
# En la consola de PostgreSQL:
CREATE DATABASE crm_db;

# 7. Inicializar base de datos
python init_db.py --init

# 8. (Opcional) Cargar datos de prueba
python init_db.py --seed

# 9. Ejecutar aplicación
python run.py

# 10. Verificar que funciona
# Abrir navegador en: http://localhost:5000/health
```

---

## Opción 2: Docker (Recomendado para Producción)

### Prerequisitos
- Docker
- Docker Compose

### Pasos

```bash
# 1. Navegar al directorio
cd crm-service

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# 3. Construir y levantar servicios
docker-compose up -d

# 4. Ver logs
docker-compose logs -f crm-service

# 5. Verificar que funciona
# Abrir navegador en: http://localhost:5002/health

# 6. Acceder al contenedor (si es necesario)
docker-compose exec crm-service bash

# 7. Detener servicios
docker-compose down
```

---

## ⚙️ Configuración de Variables de Entorno

Edita el archivo `.env` con los siguientes valores:

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=tu-secret-key-aqui-cambiar-en-produccion

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crm_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password

# JWT
JWT_SECRET_KEY=tu-jwt-secret-key-cambiar-en-produccion
JWT_ALGORITHM=HS256
AUTH_SERVICE_URL=http://localhost:5001

# File Upload
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=5242880
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,txt

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/crm-service.log

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## 🧪 Ejecutar Tests

```bash
# Activar entorno virtual primero
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Ver reporte de cobertura
# Abrir: htmlcov/index.html
```

---

## 📡 Probar API

### 1. Obtener Token JWT (desde auth-service)
```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"operador01","password":"tu_password"}'
```

### 2. Crear un Proveedor
```bash
curl -X POST http://localhost:5000/api/v1/suppliers \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -F "razon_social=Farmacéutica Ejemplo SA" \
  -F "nit=900123456-7" \
  -F "representante_legal=Juan Pérez" \
  -F "pais=Colombia" \
  -F "nombre_contacto=María García" \
  -F "celular_contacto=3001234567" \
  -F "email=contacto@ejemplo.com" \
  -F "certificado=@/ruta/a/certificado.pdf"
```

### 3. Listar Proveedores
```bash
curl -X GET "http://localhost:5000/api/v1/suppliers?page=1&per_page=10" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### 4. Buscar Proveedores
```bash
# Por país
curl -X GET "http://localhost:5000/api/v1/suppliers?pais=Colombia" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"

# Por búsqueda de texto
curl -X GET "http://localhost:5000/api/v1/suppliers?search=Farmacéutica" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### 5. Obtener Estadísticas
```bash
curl -X GET "http://localhost:5000/api/v1/suppliers/stats" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 🛠️ Comandos Útiles

```bash
# Usando Makefile
make install      # Instalar dependencias
make run          # Ejecutar aplicación
make test         # Ejecutar tests
make clean        # Limpiar archivos temporales
make docker-build # Construir imagen Docker
make docker-up    # Levantar servicios
make docker-down  # Detener servicios

# Comandos Flask directos
flask db init          # Inicializar migraciones
flask db migrate -m "mensaje"  # Crear migración
flask db upgrade       # Aplicar migraciones

# Python directos
python init_db.py --init   # Crear tablas
python init_db.py --seed   # Cargar datos de prueba
python manage.py init_db   # Inicializar BD
```

---

## 📂 Archivos Importantes

- `run.py` - Punto de entrada de la aplicación
- `.env` - Variables de entorno (NO subir a Git)
- `app/__init__.py` - Factory de Flask
- `app/modules/suppliers/` - Módulo de proveedores
- `tests/` - Tests unitarios
- `uploads/` - Archivos subidos (se crea automáticamente)
- `logs/` - Logs de la aplicación (se crea automáticamente)

---

## 🐛 Troubleshooting

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio correcto
cd crm-service
# Y de tener activado el entorno virtual
source venv/bin/activate
```

### Error: "Connection refused" (PostgreSQL)
```bash
# Verifica que PostgreSQL esté corriendo
# En Linux:
sudo systemctl status postgresql
# En Mac:
brew services list
# En Windows:
# Verificar en Servicios de Windows
```

### Error: "Table does not exist"
```bash
# Ejecutar migraciones
python init_db.py --init
# o
flask db upgrade
```

### Error: "Unauthorized" en endpoints
```bash
# Verifica que tengas un token JWT válido
# Obtén uno desde el servicio de autenticación
```

---

## 📚 Documentación Adicional

- [README.md](README.md) - Documentación general
- [API_DOCS.md](API_DOCS.md) - Documentación completa de API
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Resumen de implementación

---

## ✅ Checklist de Inicio

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL instalado y corriendo
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo .env configurado
- [ ] Base de datos creada
- [ ] Tablas inicializadas
- [ ] Aplicación corriendo
- [ ] Endpoint /health responde correctamente
- [ ] Token JWT obtenido
- [ ] Primer proveedor creado exitosamente

---

**¡Listo para empezar! 🎉**

Si tienes problemas, revisa la documentación o los logs en `logs/crm-service.log`
