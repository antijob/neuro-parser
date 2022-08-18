import requests

from django.conf import settings

API_URL = "https://dcapi.net/api/mail/"


def send_email(subject, from_email, to_email, plain_message, html_message):
    data = {
        "to": to_email,
        "fromemail": from_email,
        "text": plain_message,
        "subject": subject,
    }
    if html_message:
        data["html"] = html_message
    headers = {"Authorization": settings.EMAIL_HOST_PASSWORD}
    return requests.post(API_URL, json=data, headers=headers)
