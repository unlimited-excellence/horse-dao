import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.app = Application.builder().token(self.token).build()

        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Обробник команди /start."""
        await update.message.reply_text("Привіт! Я ваш Telegram-бот. Використовуйте /help для отримання списку команд.")

    async def help(self, update: Update, context: CallbackContext) -> None:
        """Обробник команди /help."""
        await update.message.reply_text("Список команд:\n/start - Запуск бота\n/help - Допомога")

    async def echo(self, update: Update, context: CallbackContext) -> None:
        """Відповідає тим же повідомленням, яке отримує."""
        await update.message.reply_text(f"Ви сказали: {update.message.text}")

    def run(self):
        print("Running bot...")
        self.app.run_polling()
