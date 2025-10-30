#!/bin/sh
set -e

echo "Starting Inventory Service..."

# Wait for database to be ready
echo "Waiting for database..."
until python -c "from app.config.database import db; from app import create_app; app = create_app(); app.app_context().push(); db.engine.connect()" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready"

# Run migrations (if flask-migrate is configured)
echo "Running database migrations..."
flask db upgrade || echo "No migrations to apply"

# Optional: run the init_db script when INIT_DB is set (useful for local dev)
if [ "${INIT_DB:-}" = "true" ] || [ "${INIT_DB:-}" = "1" ]; then
  echo "INIT_DB enabled - running init_db.py (this will DROP and recreate tables)"
  python init_db.py || echo "init_db.py failed"
fi

# Start application
PORT_VALUE=${PORT:-9008}
echo "Starting application on port ${PORT_VALUE}"
exec gunicorn --bind 0.0.0.0:${PORT_VALUE} \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "app:create_app()"
