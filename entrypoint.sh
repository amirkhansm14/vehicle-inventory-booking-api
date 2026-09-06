#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn vehicle_system.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
