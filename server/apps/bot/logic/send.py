from telegram import Bot
from server.settings.components.telegram import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_message(user_id, message):
    try:
        bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        print('An error occurred: ', e)
        print('Chat ID: ', user_id)

# def send_incident():

