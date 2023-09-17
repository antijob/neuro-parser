#!/bin/bash

# Wait for the PostgreSQL server to become available
while !</dev/tcp/db/5432; do sleep 1; done

# Start the Django application
python manage.py runserver 0.0.0.0:8000 &

# Start the Celery worker
celery -A server worker --loglevel=info
