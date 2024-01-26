#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
./wait-for-it.sh db:5432 -- python manage.py makemigrations

python manage.py migrate

# Seed clients
python manage.py seed_clients

# Run the Django development server
python manage.py runserver 0.0.0.0:8000
