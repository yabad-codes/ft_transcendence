#!/bin/sh

set -e

# Collect static files
python manage.py collectstatic --noinput

# Run migrations for each app
python manage.py makemigrations authentication
python manage.py makemigrations chat
python manage.py makemigrations player
python manage.py makemigrations pong
python manage.py migrate

# Start gunicorn server
gunicorn -c config/gunicorn.conf.py --reload pong_service.wsgi:application