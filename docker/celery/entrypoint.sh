#!/bin/bash

# Функция для логирования
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для завершения работы
cleanup() {
  log "Завершение работы..."
  pkill -f 'celery -A server worker'
  pkill -f 'celery -A server beat'
  exit 0
}

# Установка обработчика сигнала для корректного завершения работы
trap cleanup SIGINT SIGTERM

# Ожидание доступности сервера PostgreSQL
log "Ожидание доступности сервера PostgreSQL на db:5432..."
while ! </dev/tcp/db/5432; do
  sleep 1
done
log "PostgreSQL доступен."

# Запуск celery worker для queue crawler
log "Запуск celery worker для queue crawler..."
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server worker --loglevel=info -E -c 1 -n crawler -Q crawler &

# Запуск celery worker для queue parser
log "Запуск celery worker для queue parser..."
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server worker --loglevel=info -E -c 1 -n parser -Q parser &

# Запуск celery worker для queue bot
log "Запуск celery worker для queue bot..."
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server worker --loglevel=info -E -c 1 -n bot -Q bot &

# Запуск celery beat
log "Запуск celery beat..."
watchmedo auto-restart -d ./server/celery/ -p '*.py' -- celery -A server beat --loglevel=info

# Ожидание завершения работы
wait
