#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000