import os

import telebot

from database.database_worker import DatabaseWorker
from endpoints.telegram import TelegramBotService
from services.MiscService import MiscService
from services.UsersService import UsersService
from services.NotificationsService import NotificationsService

if __name__ == '__main__':
    print("Initializing MongoDB")
    databaseWorker = DatabaseWorker(os.getenv("MONGODB_URI"), os.getenv("MONGODB_DATABASE"))

    print("Initializing MiscService")
    misc_service = MiscService(databaseWorker)
    config = misc_service.get_or_create_config()

    print("Initializing UsersService")
    users_service = UsersService(databaseWorker)

    print("Initializing TeleBot")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telebot.TeleBot(bot_token)

    print("Initializing NotificationsService")
    notifications_service = NotificationsService(bot)

    print("Initializing Telegram Bot")
    telegram_bot_service = TelegramBotService(bot, users_service, notifications_service)

    print("Running Telegram Bot")
    telegram_bot_service.run()