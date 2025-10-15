#!/bin/sh
set -e

echo "[entrypoint] Starting auth-service entrypoint"

# Defaults (can be overridden by env)
: ${DB_HOST:=medisupply-db}
: ${DB_PORT:=5432}
: ${DB_USER:=app}

wait_for_db() {
  echo "[entrypoint] Waiting for database ${DB_HOST}:${DB_PORT}..."
  until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
    sleep 1
  done
  echo "[entrypoint] Database is ready"
}

# If DATABASE_URL provided, try to derive host/port/user (best-effort)
if [ -n "$DATABASE_URL" ]; then
  HOST_EXTRACT=$(echo "$DATABASE_URL" | sed -n 's#.*@\([^:/]*\).*#\1#p' || true)
  PORT_EXTRACT=$(echo "$DATABASE_URL" | sed -n 's#.*@[^:]*:\([0-9]*\)/.*#\1#p' || true)
  USER_EXTRACT=$(echo "$DATABASE_URL" | sed -n 's#.*//\([^:]*\):.*#\1#p' || true)
  if [ -n "$HOST_EXTRACT" ]; then DB_HOST="$HOST_EXTRACT"; fi
  if [ -n "$PORT_EXTRACT" ]; then DB_PORT="$PORT_EXTRACT"; fi
  if [ -n "$USER_EXTRACT" ]; then DB_USER="$USER_EXTRACT"; fi
fi

wait_for_db

if [ "${INIT_DB}" = "1" ] || [ "${INIT_DB}" = "true" ]; then
  echo "[entrypoint] INIT_DB is set, running database initialization"
  python init_db.py --init || echo "[entrypoint] init returned non-zero"
  python init_db.py --seed || echo "[entrypoint] seed returned non-zero"
else
  echo "[entrypoint] INIT_DB not set, skipping DB init/seed"
fi

echo "[entrypoint] Launching auth-service"
exec python app.py
