from typing import Tuple

import dateparser
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone

from server.apps.core.logic.grabber.region import region_codes


def extract_text_and_url(message: str) -> Tuple[str, str]:
    validate = URLValidator()
    *text, url = [s.strip() for s in message.split("\n") if s]

    try:
        validate(url)
        return (
            "\n".join(text),
            url,
        )
    except ValidationError:
        return "", ""


def handle_date(message: str) -> str:
    today = timezone.now().date()
    yesterday = timezone.now() - timezone.timedelta(days=1)
    date = None
    if message.lower().startswith("сегодня"):
        date = today
    elif message.lower().startswith("вчера"):
        date = yesterday
    elif message:
        date = dateparser.parse(message, languages=["ru"]) or today
    if not date:
        date = today
    return date.strftime("%Y-%m-%d")


def incident_message_to_dict(message: str):
    keywords = {
        "Дата": "date",
        "Теги": "tags",
        "Регион": "region",
        "Описание": "description",
        "Категория": "incident_type",
        "Заголовок": "title",
        "Количество": "count",
        "Источник": "url",
    }

    message = message.replace("+", "")

    result = {"manual_mode": True}

    for line in message.split(";"):
        values = line.split(":", 1)

        if len(values) != 2:
            continue

        key, value = [i.strip() for i in values]
        real_key = keywords[key]

        if real_key == "region":
            result[real_key] = region_codes(value)[0]
        elif real_key == "tags":
            result[real_key] = [tag.strip() for tag in value.split(",")]
        elif real_key == "date":
            result[real_key] = handle_date(value)
        elif real_key == "incident_type":
            try:
                result[real_key] = int(value)
            except:
                result[real_key] = 0
        else:
            result[real_key] = value

    return result
