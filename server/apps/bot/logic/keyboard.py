from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from server.apps.core.models import Article


def edit_incident_markup(article: Article) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("✏️ Редактировать", url=article.get_incident_url())],
        ]
    )
