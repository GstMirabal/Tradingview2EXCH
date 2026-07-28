#!/bin/bash
set -euo pipefail

export $(grep -v '^#' .env | xargs)

cd backend

python -u manage.py migrate

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000