"""
TODO: Remove this unused module
"""

import re
import string

import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from server.apps.core.models import Article
from server.apps.core.tasks import search_duplicates

PRINTABLE_CHARS = frozenset(string.printable)

TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_ID = ''
TELEGRAM_URL = "https://api.telegram.org/bot{}".format(TELEGRAM_BOT_TOKEN)
ALLOWED_CHAT_IDS = [TELEGRAM_CHAT_ID]
ALLOWED_USERNAMES = []


def command_add(command, host, message):
    incident = created = None
    query_message_id = message["message_id"]
    chat_id = message["chat"]["id"]

    # Url only
    if is_valid_url(command):
        incident, created = add_incident(url=command)

    # Url and text
    lines = command.split("\n")
    if len(lines) > 1:
        if is_valid_url(lines[0]):
            incident, created = add_incident(url=lines[0],
                                             text="\n".join(lines[1:]))
        elif is_valid_url(lines[-1]):
            incident, created = add_incident(url=lines[-1],
                                             text="\n".join(lines[:-1]))

    # Text only
    if not incident:
        if message.get("forward_from_chat") or len(command) > 50:
            url = telegram_message_url(message)
            incident, created = add_incident(telegram_url=url, text=command)

    if incident:
        send_created_message(incident, created, chat_id, host, query_message_id)
        return incident
    else:
        msg = (
            "Не удалось создать инцидент"
        )
        send_message(msg, chat_id, query_message_id=query_message_id)
        return True


def telegram_message_url(message):
    if not is_forwarded(message):
        return
    forward_chat = message['forward_from_chat']['username']
    forward_id = message['forward_from_message_id']
    return 'https://t.me/{0}/{1}'.format(forward_chat, forward_id)


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               "\U0001F600-\U0001F64F"  # emoticons
                               "\U0001F300-\U0001F5FF"  # symbols & pictographs
                               "\U0001F680-\U0001F6FF"  # transport & map symbols
                               "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "\U00002702-\U000027B0"
                               "\U000024C2-\U0001F251"
                               "\U0001f926-\U0001f937"
                               "\u200d"
                               "\u2640-\u2642"
                               "]+", flags=re.UNICODE)
    return re.sub(emoji_pattern, '', text)


def send_created_message(incident, created, chat_id, host, query_message_id):
    dashboard_url = incident.get_absolute_url()
    if not created:
        msg = ("Данный инцидент уже был добавлен ранее.\n"
               "Редактировать: https://{0}{1}").format(host,
                                                       dashboard_url)
        send_message(msg, chat_id, query_message_id=query_message_id)
        return True

    msg = ("Добавлен инцидент:\n<b>{0}</b>\n\n"
           "Редактировать: https://{1}{2}").format(incident.any_title(),
                                                   host,
                                                   dashboard_url)
    send_message(msg, chat_id)
    return True


def send_message(message,
                 chat_id,
                 disable_web_page_preview=True,
                 query_message_id=None):
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview,
        "reply_to_message_id": query_message_id
    }
    url = "{url}/sendMessage".format(url=TELEGRAM_URL)
    response = requests.post(url, json=data)
    response_data = response.json()

    if response_data['error_code'] == 400:
        data.pop("reply_to_message_id", None)

    requests.post(url, json=data)


def is_valid_url(url):
    validate = URLValidator()
    url = "".join(filter(lambda ch: ch in PRINTABLE_CHARS, url))
    try:
        validate(url)
        return not url.startswith("https://t.me/")
    except ValidationError:
        return False


def create_incident_from_article(article):
    exists = article.is_incident_created
    if exists:
        incident = article.incident
    else:
        if not article.is_downloaded:
            article.download()
        incident = article.create_incident()
    return incident, not exists


def add_incident(url=None, text=None, telegram_url=None):
    if url:
        incident, created = incident_by_url(url, text)
    elif telegram_url and text:
        incident, created = incident_by_telegram_url(telegram_url, text)
    elif text and len(text) > 100:
        incident, created = incident_by_text(text)
    else:
        return None, None

    if incident and created:
        search_duplicates.delay(incident.article.id)
    return incident, created


def incident_by_url(url, text):
    article, article_created = Article.objects.get_or_create(url=url)
    if article_created and text and len(text) > 150:
        article.text = text
        article.save(update_fields=['text'])
    return create_incident_from_article(article)


def incident_by_telegram_url(telegram_url, text):
    article = Article.objects.filter(text=text).first()
    if not article:
        article, article_created = (Article.objects
                                    .get_or_create(url=telegram_url))
        if article_created:
            article.text = text

    article.url = telegram_url
    article.is_downloaded = True
    article.save(update_fields=['text', 'is_downloaded', 'url'])
    if article.is_incident_created:
        article.incident.description = text
        article.incident.urls = [telegram_url]
        article.incident.save(update_fields=['description', 'urls'])
        return article.incident, False
    return create_incident_from_article(article)


def incident_by_text(text):
    article, _ = Article.objects.get_or_create(text=text)
    if article.is_incident_created:
        return article.incident, False
    article.title = get_title(text)
    article.is_downloaded = True
    article.save(update_fields=["title", "is_downloaded"])
    return create_incident_from_article(article)


def get_title(text):
    paragraphs = [paragraph
                  for paragraph in re.split(r"\n", text)
                  if paragraph]
    if len(paragraphs) > 1:
        return paragraphs[0]
    sentences = [sentence
                 for sentence in re.split(r"\.", text)
                 if sentence]
    return sentences[0]


def is_forwarded(message):
    forward_chat = message.get('forward_from_chat')
    if not forward_chat:
        return False
    forward_chat_type = forward_chat["type"]
    if forward_chat_type != "channel":
        return False
    return True
