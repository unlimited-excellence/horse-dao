import hashlib
import logging
import os
import threading
import time

import telebot

from database.database_worker import DatabaseWorker
from endpoints.telegram import TelegramBotService
from services.MiscService import MiscService
from services.UsersService import UsersService
from services.NotificationsService import NotificationsService
from services.CodeforcesService import CodeforcesService

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    assert os.getenv("MONGODB_URI") is not None, "MONGODB_URI environmental variable is not set"
    assert os.getenv("MONGODB_DATABASE") is not None, "MONGODB_DATABASE environmental variable is not set"
    
    logging.info("Hello, Denys!")
    time_hash = time.time()
    logging.info(time_hash)
    logging.info(f"123456/contest.list?apiKey=KEY&time={time_hash}&gym=false#SECRET")
    logging.info(hashlib.sha3_512(f"123456/contest.list?apiKey=KEY&time={time_hash}&gym=false#SECRET".encode()).hexdigest())

    logging.info("Initializing MongoDB")
    databaseWorker = DatabaseWorker(os.getenv("MONGODB_URI"), os.getenv("MONGODB_DATABASE"))

    logging.info("Initializing MiscService")
    misc_service = MiscService(databaseWorker)
    config = misc_service.get_or_create_config()

    logging.info("Initializing TeleBot")
    bot_token = config["telegram"]["BOT_TOKEN"]
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