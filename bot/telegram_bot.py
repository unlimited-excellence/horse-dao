import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)

from services.user_service import UserService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, user_service: UserService):
        # Validate environment variables
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

        self.user_service = user_service

        try:
            self.app = Application.builder().token(self.token).build()

            # Add command and message handlers
            self.app.add_handler(CommandHandler("start", self.start))
            self.app.add_handler(CommandHandler("help", self.help))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

            # Add a global error handler
            self.app.add_error_handler(self.error_handler)
        except Exception as e:
            logger.error("Failed to initialize Telegram bot", exc_info=e)
            raise

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Handler for /start command."""
        try:
            if update.message:
                user = update.message.from_user
                if not user or not user.id:
                    await update.message.reply_text("User info unavailable.")
                    return
                registration_message = self.user_service.register_user(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                await update.message.reply_text(registration_message)
        except Exception as e:
            logger.error("Error in start handler", exc_info=e)
            if update.message:
                await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    async def help(self, update: Update, context: CallbackContext) -> None:
        """Handler for /help command."""
        try:
            if update.message:
                await update.message.reply_text("List of commands:\n/start - Start the bot\n/help - Get help")
        except Exception as e:
            logger.error("Error in help handler", exc_info=e)
            if update.message:
                await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    async def echo(self, update: Update, context: CallbackContext) -> None:
        """Echo back the message received."""
        try:
            if not update.message or not update.message.text:
                return

            # Validate input length
            if len(update.message.text) > 4096:  # Telegram's message length limit
                await update.message.reply_text("Message too long. Please send a shorter message.")
                return

            # Sanitize input for display
            sanitized_text = update.message.text.replace('<', '&lt;').replace('>', '&gt;')
            await update.message.reply_text(f"You said: {sanitized_text}")
        except Exception as e:
            logger.error("Error in echo handler", exc_info=e)
            if update.message:
                await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    async def error_handler(self, update: object, context: CallbackContext) -> None:
        """Global error handler."""
        logger.error("Exception while handling an update:", exc_info=context.error)

    def run(self):
        logger.info("Running bot...")
        self.app.run_polling()

    def stop(self):
        """Stop the bot gracefully."""
        if self.app.running:
            logger.info("Stopping bot...")
            self.app.stop()
            self.app.shutdown()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
