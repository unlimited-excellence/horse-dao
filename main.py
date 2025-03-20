import logging
import os
import threading

import telebot

from database.database_worker import DatabaseWorker
from endpoints.telegram import TelegramBotService
from services.MiscService import MiscService
from services.UsersService import UsersService
from services.NotificationsService import NotificationsService
from services.CodeforcesService import CodeforcesService

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Hello, World!")

    logging.info("Initializing MongoDB")
    databaseWorker = DatabaseWorker(os.getenv("MONGODB_URI"), os.getenv("MONGODB_DATABASE"))

    logging.info("Initializing MiscService")
    misc_service = MiscService(databaseWorker)
    config = misc_service.get_or_create_config()

    logging.info("Initializing TeleBot")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telebot.TeleBot(bot_token)

    logging.info("Initializing NotificationsService")
    notifications_service = NotificationsService(bot)

    logging.info("Initializing UsersService")
    users_service = UsersService(databaseWorker, notifications_service)

    logging.info("Initializing Telegram Bot")
    telegram_bot_service = TelegramBotService(bot, users_service, notifications_service, config)

    logging.info("Initializing CodeforcesService")
    codeforces_service = CodeforcesService(databaseWorker, users_service, config)
    codeforces_thread = threading.Thread(target=codeforces_service.mainloop)
    codeforces_thread.start()

    logging.info("Running Telegram Bot")
    telegram_bot_service.run()