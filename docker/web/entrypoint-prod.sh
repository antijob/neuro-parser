#!/bin/bash

# Wait for the PostgreSQL server to become available
while !</dev/tcp/db/5432; do sleep 1; done

# Apply database migrations
python manage.py migrate

# Set webhook
python manage.py set_webhook

# Run the status update script
python manage.py status_update

# Start the Django application
gunicorn --bind 0.0.0.0:8000 server.wsgi


