#!/bin/bash

# Остановить сервер
docker-compose down -v

# Поднять сервер с новой базой данных
docker-compose up -d

# Пересоздать рабочую базу с нуля
docker-compose exec db psql -U postgres -d postgres -c 'DROP DATABASE "neural-parser";'
docker-compose exec db psql -U postgres -d postgres -c 'CREATE DATABASE "neural-parser";'

# Применить миграции
# docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser --noinput --email np@np.com
