from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from server.apps.core.incident_types import IncidentType
from server.apps.bot.logic.messages import (
    CATEGORIES_MESSAGE,
)
from server.apps.bot.models import Channel, TypeStatus


def create_inline_keyboard(chn: Channel):
    """
    Creates inline keyboard for all types of incidents that we have in IncidentType model.
    """

    cross = "\U0000274c"
    check = "\U00002705"

    types = TypeStatus.objects.filter(
        channel=chn, incident_type__should_sent_to_bot=True
    ).order_by("id")

    keyboard = list()

    for item in types:
        btn_label = item.incident_type.description
        if item.status:
            status = check
        else:
            status = cross

        keyboard.append(
            [
                InlineKeyboardButton(
                    btn_label, callback_data=str(item.incident_type.id)
                ),
                InlineKeyboardButton(status, callback_data=str(item.incident_type.id)),
            ]
        )

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

    chn = Channel.objects.get(channel_id__exact=query.message.chat_id)

    # Extract the callback_data which contains the button information
    button_data = query.data
    print("BUTTON DATA", button_data)
    incident_type = IncidentType.objects.get(id__exact=int(button_data))
    type_status = TypeStatus.objects.get(incident_type=incident_type, channel=chn)
    type_status.status = not type_status.status
    type_status.save()

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_inline_keyboard(chn),  # Update the inline keyboard
    )
