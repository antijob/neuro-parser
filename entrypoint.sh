#!/bin/bash

while !</dev/tcp/db/5432; do sleep 1; done

python manage.py runserver 0.0.0.0:8000 &
celery -A server beat --loglevel=info &
celery -A server worker --loglevel=info 
