#!/bin/sh
set -e
if [ "${INIT_DB:-}" = "true" ] || [ "${INIT_DB:-}" = "1" ]; then
  python init_db.py
fi
exec "$@"
