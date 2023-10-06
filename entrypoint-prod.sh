#!/bin/bash

# Wait for the PostgreSQL server to become available
while !</dev/tcp/db/5432; do sleep 1; done

# Start the Django application
gunicorn --bind 0.0.0.0:8000 server.wsgi