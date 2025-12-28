#!/bin/bash

# Wait for DB
while ! nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 0.5
done

# Apply Migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect Static Files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
# -w 4: 4 Worker processes (Optimized for standard 2-core cloud instances)
# -b: Bind address
echo "Starting Gunicorn..."

# Start Gunicorn with a timeout that matches Nginx
exec gunicorn core.wsgi:application \
    --workers 4 \
    --timeout 10 \
    --bind 0.0.0.0:8000