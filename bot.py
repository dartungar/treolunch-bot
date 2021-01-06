from telegram.ext import Updater, CommandHandler
from telegram import ReplyKeyboardMarkup

import logging
import choose_place
import os

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

place_chooser = choose_place.PlaceChooser()

keyboard = ReplyKeyboardMarkup([['/start']], True)


def main():

    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    def get_place(update, context):
        place = place_chooser.get_full_info()
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=place, reply_markup=keyboard)

    start_handler = CommandHandler('start', get_place)
    dispatcher.add_handler(start_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()