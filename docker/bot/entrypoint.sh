#!/bin/bash

# Define the database host and port
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

# Log function for better readability
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Wait for the PostgreSQL server to become available
log "Waiting for PostgreSQL to become available at $DB_HOST:$DB_PORT..."
for i in {1..60}; do
  if </dev/tcp/$DB_HOST/$DB_PORT; then
    log "PostgreSQL is available."
    break
  fi
  if [ $i -eq 60 ]; then
    log "PostgreSQL is not available after 60 seconds, exiting."
    exit 1
  fi
  sleep 1
done

# Run the bot
log "Running the bot..."
python -m server.apps.bot.bot
