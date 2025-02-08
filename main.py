import os

from endpoints.telegram import TelegramBotService

if __name__ == '__main__':
    print("Initializing Telegram Bot")
    telegram_bot_service = TelegramBotService(os.getenv("TELEGRAM_BOT_TOKEN"))

    print("Running Telegram Bot")
    telegram_bot_service.run()