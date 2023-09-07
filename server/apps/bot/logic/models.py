from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from telegram import Update

# from server.apps.bot.logic.keyboard import edit_incident_markup
from server.apps.core.models import Article, MediaIncident


def create_incident(update: Optional[Update] = None, **kwargs: Any):
    url = kwargs.get("url")
    text = kwargs.get("text")
    title = kwargs.get("title")
    date = kwargs.get("date")
    tags = kwargs.get("tags")
    count = kwargs.get("count")
    region = kwargs.get("region")
    incident_type = kwargs.get("incident_type")
    description = kwargs.get("description")
    manual_mode = kwargs.get("manual_mode", False)

    validate = URLValidator()

    try:
        validate(url)
    except ValidationError:
        update.message.reply_text("Ошибка при создании: некорректный URL-адрес.")
        return

    if manual_mode:
        incident = MediaIncident.objects.filter(urls__contains=[url]).first()

        if incident:
            update.message.reply_text("Инцидент с таким источником уже существует.")
            return

        article, created = Article.objects.get_or_create(
            url=url,
            title=title,
            text=description,
            publication_date=date,
            is_downloaded=True,
        )

        if count.isdigit():
            count = int(count)
        else:
            count = 1

        public_title = title

        incident = MediaIncident.objects.create(
            urls=[url],
            status=MediaIncident.UNPROCESSED,
            title=title,
            description=description,
            public_title=public_title,
            public_description=description,
            create_date=date,
            region=region,
            count=count,
            tags=tags,
        )
        incident.incident_type = incident_type
        article.is_incident_created = True
        article.incident = incident
        article.save()

        message = (
            "Создан инцидент:\n\n"
            "<b>Заголовок:</b>\n{title}\n"
            "<b>Описание:</b>\n{description}\n"
            "<b>Количество:</b> {count}\n"
            "<b>Дата:</b> {date}\n"
            "<b>Регион:</b> {region}\n"
            "<b>Теги:</b> {tags}\n"
            "<b>Категория:</b> {incident_type}\n"
            "<b>Источник:</b> {url}\n\n"
        ).format(
            title=incident.public_title,
            description=incident.get_description(),
            region=incident.region_name(),
            date=incident.create_date,
            url=", ".join(incident.urls),
            edit_url=incident.get_absolute_url(),
            count=incident.count,
            incident_type=incident.get_incident_type_display(),
            tags=", ".join(incident.tags),
        )
        update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=edit_incident_markup(incident.article),
        )
    else:
        article, created = Article.objects.get_or_create(url=url)

        if text:
            article.text = f"{text}\n\nИсточник: {url}"
            article.save(update_fields=["text"])

        if not article.is_downloaded:
            article.download()

        if not article.is_incident_created:
            article.create_incident()

        if created:
            created_message = "Инцидент создан"
            if article.incident and article.incident.title:
                created_message = f"{created_message}: <b>{article.incident.title}</b>"
            else:
                created_message = f"{created_message}."

            update.message.reply_text(
                created_message,
                reply_markup=edit_incident_markup(article),
                parse_mode="HTML",
            )
        else:
            update.message.reply_text("Инцидент с таким источником уже существует.")
