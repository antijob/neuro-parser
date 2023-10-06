#!/bin/bash

# Wait for the PostgreSQL server to become available
while !</dev/tcp/db/5432; do sleep 1; done

celery -A server worker --loglevel=info -E -c 1 -n crawler -Q crawler &
celery -A server worker --loglevel=info -E -c 1 -n parser  -Q parser  &
celery -A server beat   --loglevel=info

