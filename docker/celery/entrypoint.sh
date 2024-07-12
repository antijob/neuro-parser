#!/bin/bash

# Wait for the PostgreSQL server to become available
while !</dev/tcp/db/5432; do sleep 1; done

watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server worker --loglevel=info -E -c 1 -n crawler -Q crawler &
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server worker --loglevel=info -E -c 1 -n parser  -Q parser  &
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server beat   --loglevel=info


