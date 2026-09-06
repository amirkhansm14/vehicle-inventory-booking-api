release: python manage.py migrate --noinput
web: gunicorn vehicle_system.wsgi:application --log-file -
