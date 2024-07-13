#!/bin/sh

set -e

# Run migrations for each app
python manage.py makemigrations authentication
python manage.py makemigrations chat
python manage.py makemigrations player
python manage.py makemigrations pong
python manage.py migrate

# Start gunicorn server
gunicorn -c config/gunicorn.conf.py pong_service.wsgi:application