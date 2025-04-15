#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Create superuser..."
manage.py create_superuser

echo "Seeding the database..."
python manage.py seed

echo "Release phase completed."
