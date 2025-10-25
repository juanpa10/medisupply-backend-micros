#!/bin/bash
set -e

echo "🚀 Starting Inventory Service..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
until python -c "from app.config.database import db; from app import create_app; app = create_app(); app.app_context().push(); db.engine.connect()" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "✅ Database is ready!"

# Run migrations
echo "📦 Running database migrations..."
flask db upgrade || echo "⚠️  No migrations to apply"

# Start application
echo "🎯 Starting application on port ${PORT:-5003}..."
exec gunicorn --bind 0.0.0.0:${PORT:-5003} \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "app:create_app()"
