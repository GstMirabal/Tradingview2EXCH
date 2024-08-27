#!/bin/bash

export $(grep -v '^#' .env | xargs)

echo "DEBUG=$DEBUG"
echo "ALLOWED_HOSTS=$ALLOWED_HOSTS"
echo "LOCAL_HOST=$LOCAL_HOST"
echo "EMAIL_HOST=$EMAIL_HOST"
echo "EMAIL_PORT=$EMAIL_PORT"
echo "EMAIL_HOST_USER=$EMAIL_HOST_USER"
echo "EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD"
echo "DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL"
echo "LOG_LEVEL=$LOG_LEVEL"
echo "ENGINE=$ENGINE"
echo "NAME=$NAME"
echo "API_KEY=$API_KEY"
echo "API_SECRET=$API_SECRET"

python -u manage.py makemigrations

python -u manage.py migrate

python -u manage.py runserver 0.0.0.0:8000