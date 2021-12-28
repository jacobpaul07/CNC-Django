#!/bin/bash

# Collect static files
# echo "Collect static files"
# python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations webapi"
python manage.py makemigrations Webapp
python manage.py makemigrations 

echo "Apply database migrations project"
python manage.py migrate Webapp
python manage.py migrate

# Start server
echo "Starting server"
# python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
