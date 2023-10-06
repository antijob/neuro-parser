from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from server.apps.core.incident_types import IncidentType
from server.apps.bot.logic.messages import (
    CATEGORIES_MESSAGE,
)
from server.apps.bot.models import Channel, TypeStatus

def get_categ_list() -> str:
    """
    Return formated string with
    message for keyboard and with
    all categories from IncidentType model inserted
    """
    categories = IncidentType.objects.all()
    msg = ''
    for i, cat in enumerate(categories):
        msg += f'{i+1} - {cat.description} \n'

    categories_message_formated = CATEGORIES_MESSAGE.format(
            incidents = msg
            )

    return categories_message_formated

def create_inline_keyboard(chn: Channel):
    """
    Creates inline keyboard for all types of incidents that we have in IncidentType model.

    cats - Channel object for channel were we creating a keyboard
    so we can grab settings for it

    if we need more buttons and rows of them
    we need to use list of lists [[], []]
    where each inner list - one row in keyboard
        text and data format for buttons
        1  - off
        1* - on
    """

    types = TypeStatus.objects.filter(channel=chn)

    keys = list()

    for i, tp in enumerate(types):
        if tp.status:
            bt_text = str(i+1) + "*"
        else:
            bt_text = str(i+1)
        inc_name = tp.incident_type.description
        keys.append(InlineKeyboardButton(bt_text, callback_data=inc_name+'|'+bt_text))

    keyboard = list()

    if len(keys) > 5:
        keyboard.append(keys[0:5])
        keyboard.append(keys[5:])
    else:
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
    print("BUTTON DATA", button_info)

    # find inc type object that corresponds pressed button
    # and then TypeStatus object than connects channel and incident type
    inc_type = IncidentType.objects.get(description__exact=button_info.split('|')[0])
    ts = TypeStatus.objects.get(
            incident_type = inc_type,
            channel = cats
            )
    if '*' in button_info:
        setattr(ts, 'status', False)
    else:
        setattr(ts, 'status', True)

    ts.save()

    # Edit the message text to update the button text

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=get_categ_list(),
        parse_mode = 'HTML',
        reply_markup=create_inline_keyboard(cats)  # Update the inline keyboard
    )

