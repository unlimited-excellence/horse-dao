from db.client import MongoDbClient
from bot.client import TelegramBot

if __name__ == '__main__':
    db_client = MongoDbClient()

    bot = TelegramBot()
    bot.run()