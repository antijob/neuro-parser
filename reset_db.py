#!/usr/bin/env python3

import argparse
import subprocess
import sys
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(command):
    logger.info(f"Executing command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error executing command: {command}")
        logger.error(result.stderr)
        sys.exit(1)
    logger.debug(f"Command output: {result.stdout}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(
        description="Reset database and optionally restore dump"
    )
    parser.add_argument(
        "-r",
        "--restore",
        action="store_true",
        help="restore dump after resetting database",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose output"
    )
    parser.add_argument(
        "-m", "--migrate", action="store_true", help="migrate existed migration files"
    )
    parser.add_argument(
        "-n", "--makemigrations", action="store_true", help="update migration files"
    )
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting database reset process")

    # Остановить сервер
    run_command("docker-compose down -v")

    # Поднять сервер с новой базой данных
    run_command("docker-compose up -d")

    # Пересоздать рабочую базу с нуля
    run_command(
        "docker-compose exec db psql -U postgres -d postgres -c 'DROP DATABASE \"neural-parser\";'"
    )
    run_command(
        "docker-compose exec db psql -U postgres -d postgres -c 'CREATE DATABASE \"neural-parser\";'"
    )

    # Если флаг установлен, восстанавливаем дамп
    if args.restore:
        logger.info("Restoring database dump")
        run_command(
            "docker-compose exec db psql -U postgres -d neural-parser -f /code/dump.sql"
        )

    # Обновить миграции
    if args.makemigrations:
        logger.info("Making migrations")
        run_command("docker-compose exec web python manage.py makemigrations")

    # Применить миграции
    if args.migrate:
        logger.info("Migrating")
        run_command("docker-compose exec web python manage.py migrate")

    run_command(
        "docker-compose exec web python manage.py createsuperuser --noinput --email np@np.com"
    )

    logger.info("Database reset process completed successfully")


if __name__ == "__main__":
    main()
