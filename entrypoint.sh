#!/bin/sh
set -e

echo "[DEVOPS] Attente et exécution des migrations Alembic..."
alembic upgrade head

echo "[DEVOPS] Démarrage du serveur de production Gunicorn..."
exec "$@"
