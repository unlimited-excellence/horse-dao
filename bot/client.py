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
        """Handler for /start command."""
        try:
            await update.message.reply_text("Hello! I'm your Telegram bot. Use /help to get a list of commands.")
        except Exception as e:
            print(f"Error in start handler: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    async def help(self, update: Update, context: CallbackContext) -> None:
        """Handler for /help command."""
        try:
            await update.message.reply_text("List of commands:\n/start - Start the bot\n/help - Get help")
        except Exception as e:
            print(f"Error in help handler: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    async def echo(self, update: Update, context: CallbackContext) -> None:
        """Відповідає тим же повідомленням, яке отримує."""
        await update.message.reply_text(f"Ви сказали: {update.message.text}")

    def run(self):
        print("Running bot...")
        self.app.run_polling()

    def stop(self):
        """Stop the bot gracefully."""
        if self.app.running:
            print("Stopping bot...")
            self.app.stop()
            self.app.shutdown()
