FROM python:3.9-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  TRANSFORMERS_CACHE=/tmp

# Установка рабочей директории
WORKDIR /code

# Копирование файла requirements.txt и установка зависимостей
COPY requirements.txt /code/
RUN pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "-c", "./entrypoint-dev.sh"]
