from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dataclasses import dataclass
from server.apps.bot.logic.messages import (
    CATEGORIES_MESSAGE,
)
from server.apps.bot.models import Channel


def create_inline_keyboard(cats: Channel):
    """
    Creates inline keyboard from dataclass
    if we need more buttont and rows of them
    we need to use list of lists [[], []]
    where each inner list - one row in keyboard
        text and data format for buttons
        1  - off
        1* - on
    """

    keys = []

    for name,value in cats.__dict__.items():
        if not name.startswith('cat'):
            continue
        cat_number = name.split('_')[1]
        if value:
            bt_text = cat_number + "*"
        else:
            bt_text = cat_number
        keys.append(InlineKeyboardButton(bt_text, callback_data=bt_text))

    keyboard = [keys]
    return InlineKeyboardMarkup(keyboard)

# Callback function to handle button presses
def button(update, context):
    """
    Callback function for pressing button on inline keyboard
    Each press cycle True and False values in dataclass
    and it changes text on buttons
    """
    query = update.callback_query
    query.answer()

    cats = Channel.objects.get(channel_id__exact=query.message.chat_id)

    # Extract the callback_data which contains the button information
    button_info = query.data
    if '*' in button_info:
        cat_number = button_info.replace('*', '')
        attr_name = 'cat_' + cat_number
        setattr(cats, attr_name, False)
    else:
        cat_number = button_info
        attr_name = 'cat_' + cat_number
        setattr(cats, attr_name, True)

    cats.save()

    # Edit the message text to update the button text
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=CATEGORIES_MESSAGE,
        parse_mode = 'HTML',
        reply_markup=create_inline_keyboard(cats)  # Update the inline keyboard
    )

