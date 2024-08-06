#!/bin/bash

# Function to run a command and check for errors
run_command() {
  echo "Executing: $1"
  if ! eval "$1"; then
    echo "Error executing command: $1" >&2
    exit 1
  fi
}

# Stop the server
run_command "docker-compose down -v"

# Start the server with a new database
run_command "docker-compose up -d"

# Wait for db initialization
echo "Waiting for db initialization..."
sleep 30

# Recreate the working database from scratch
run_command "docker-compose exec db psql -U postgres -d postgres -c 'DROP DATABASE IF EXISTS \"neural-parser\";'"
run_command "docker-compose exec db psql -U postgres -d postgres -c 'CREATE DATABASE \"neural-parser\";'"

# Restore db dump
run_command "docker-compose exec db psql -U postgres -d neural-parser -f /code/dump.sql"

# Apply migrations
# run_command "docker-compose exec web python manage.py migrate"

# Create superuser
run_command "docker-compose exec web python manage.py createsuperuser --noinput --email np@np.com"

# Apply fixtures
# run_command "docker compose exec web python manage.py loaddata incident_types.json"

echo "Database reset process completed successfully"
