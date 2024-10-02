# Руководство по разработке

Этот документ содержит инструкции для разработчиков, в том числе управление Python-пакетами, запуск проекта локально и в продакшене, настройку Telegram-бота, рассылку сообщений и использование API.

## Оглавление
1. [Управление Python-пакетами](#managing-python-packages)
2. [Локальный запуск](#local-run)
3. [Запуск в продакшене](#production-run)
4. [Настройка Telegram-бота](#telegram-bot-setup)
5. [API моделей](#model-api)
6. [REST API интерфейс](#rest-api)
7. [Инфраструктура](#infrastructure)
8. [Внесение вклада](#contributing)
9. [Контакты](#contacts)

---

## Управление Python-пакетами {#managing-python-packages}

Для управления Python-пакетами мы используем [PDM](https://pdm-project.org/):

```bash
# установка всех зафиксированных пакетов из файла блокировки
pdm install

# разрешение всех зависимостей и фиксация пакетов в lock-файл
pdm lock

# обновление всех пакетов
pdm update

# добавление нового пакета в pyproject.toml без создания venv
pdm add --no-sync <package_name>
```

Файлы `pyproject.toml` и `pdm.lock` должны быть включены в git.

---

## Локальный запуск {#local-run}

1. Создайте файл `.env` на основе `.env.template` и инициализируйте базу данных.
2. Выполните следующую команду в корневом каталоге для запуска локального контейнера:

```bash
docker-compose up -d
```

3. Добавьте следующие строки в файл `/etc/hosts` для разрешения локальных доменов Traefik:

```bash
127.0.0.1 report.local
127.0.0.1 flower-report.local
```

4. Доступ к административной панели: `http://report.local/s/ecret/admin` или используйте API: `http://report.local/api`.

5. Для начала полноценной работы системы нужно добавить ссылки на источники и типы инцидентов для отслеживания

---

## Запуск в продакшене {#production-run}

1. Измените файл `config/.env` и создайте базу данных.
2. Выполните следующую команду в корневом каталоге для запуска контейнера в продакшене:

```bash
docker-compose -f docker-compose.prod.yaml up -d
```

---

## Настройка Telegram-бота {#telegram-bot-setup}

Вы можете использовать Telegram-бота для получения уведомлений о новых инцидентах.

### Настройка

1. Зарегистрируйте нового бота через [BotFather](https://t.me/BotFather).
2. Добавьте следующие настройки в файл `.env`:

```bash
TELEGRAM_BOT_TOKEN=
```

- `TELEGRAM_BOT_TOKEN` - Токен, выданный BotFather.

3. Создайте новый чат в Telegram, добавьте бота, он его запомнит и будет присылать туда оповщенеия о новых инцидентах.
4. Чтобы получать уведомления только по определённым категориям, используйте команду `/categ` в чате.
5. Вы также можете управлять каналами через админ-панель Django в разделе Bot.

---

## API моделей {#model-api}

Для вызова внешних моделей используется [Replicate.com](https://replicate.com/), что является более дешёвой альтернативой ChatGPT.

---

## REST API интерфейс {#rest-api}

Сделан на базе `django-rest-api-framework` документация автоматически генерируется swagger и доступна по пути `/swagger-ui`

---

## Инфраструктура {#infrastructure}

Для работы проекта были созданы две удалённые машины для окружений `stage` и `prod`. 
Они настроены одинаково, сервер запускается так же, как и локально:

```
docker compose -f docker-compose.prod.yaml pull
docker-compose -f docker-compose.prod.yaml -d
```

Более подробный процесс разворачивания можно увидеть в [deploy.yml](.github/workflows/deploy.yml).

> [!NOTE] На заметку
> Рабочая директория на серверах, где расположена запущенная версия сервера: `/opt/services/neuro-parser`. 
> Актуальная информация о месте запуска сервера находится в `$DEPLOY_LOCATION` в файле [deploy.yml](.github/workflows/deploy.yml).

> [!WARNING] Важно! 
> Рабочая директория `github-actions` (`/home/github-actions/_work/neuro-parser`) используется только для клонирования репозитория.
> В ней не запускается и не должен запускаться проект.

### Типовые операции на серверах

- **На окружении (`stage` или `prod`) какая-то ошибка, нужно почитать логи**
  
  ```bash
  # почитать логи с конкретного контейнера
  # web - сервер (админка), bot - TG-бот, celery - задачи в очередях
  docker logs neuro-parser-web-1
  # или
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml logs -f
  ```

- **Нужно протестировать скрипт внутри контейнера**
  
  ```bash
  # web - сервер (админка), bot - TG-бот, celery - задачи в очередях
  docker exec -it neuro-parser-web-1 bash
  # или
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml exec -it web bash
  ```

- **Закончилось место. Сервер спамит ошибками `No space left on disk`.**

  Скорее всего, место закончилось из-за постоянной сборки или скачивания образов. Они должны чиститься периодически, однако в редких случаях этого может быть недостаточно. Можно попробовать почистить место вручную:

  ```bash
  docker container prune -f
  docker image prune -af
  # проверить место на диске
  df -h
  ```

---

## Внесение вклада {#contributing}

Мы приветствуем участие сообщества. Пожалуйста, следуйте инструкциям в файле [CONTRIBUTING.md](https://github.com/antijob/neuro-parser/blob/main/CONTRIBUTING.md).

---

## Контакты {#contacts}

Если у вас есть вопросы или требуется помощь, свяжитесь с нами по адресу info@antijob.net.
