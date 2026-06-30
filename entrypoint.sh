#!/bin/sh
set -e

mkdir -p /app/logs

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
