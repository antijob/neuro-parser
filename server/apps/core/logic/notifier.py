import requests
from django.conf import settings


def slack_message_legal_aid(message: str = None) -> bool:
    response = requests.post(
        url="https://hooks.slack.com/services/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",
        json={"text": message, "mrkdw": True, "username": "Blog"},
        timeout=5,
    )

    if response.status_code == 200:
        return True

    return False
