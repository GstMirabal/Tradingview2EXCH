#!/bin/bash
set -euo pipefail

# Only needed for a manual/local run — docker-compose's `env_file` already
# injects these into the container environment directly, without a .env
# file present in the image (deliberately not COPY'd, see .dockerignore).
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

cd backend

python -u manage.py migrate

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000