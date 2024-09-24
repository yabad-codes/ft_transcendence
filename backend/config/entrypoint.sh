#!/bin/sh

set -e

# Collect static files
python manage.py collectstatic --noinput

# Run migrations for each app
python manage.py makemigrations authentication --noinput
python manage.py makemigrations chat --noinput
python manage.py makemigrations player --noinput
python manage.py makemigrations pong --noinput
python manage.py migrate --noinput

# Start gunicorn server
gunicorn -c config/gunicorn.conf.py --reload pong_service.wsgi:application