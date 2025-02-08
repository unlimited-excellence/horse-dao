import os

from database.database_worker import DatabaseWorker
from endpoints.telegram import TelegramBotService

if __name__ == '__main__':
    print("Initializing Telegram Bot")
    telegram_bot_service = TelegramBotService(os.getenv("TELEGRAM_BOT_TOKEN"))

    print("Initializing MongoDB")
    databaseWorker = DatabaseWorker(os.getenv("MONGODB_URI"), os.getenv("MONGODB_DATABASE"))

    print("Running Telegram Bot")
    telegram_bot_service.run()