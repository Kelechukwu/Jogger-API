#!/bin/sh
pipenv run python manage.py makemigrations --noinput
pipenv run python manage.py migrate
exec "$@"