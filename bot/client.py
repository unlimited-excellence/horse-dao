import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

class TelegramBot:
    def __init__(self):
        # Validate environment variables
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
        
        try:
            self.app = Application.builder().token(self.token).build()
            
            # Add handlers with rate limiting
            self.app.add_handler(CommandHandler(
                "start",
                self.start,
                block=True,
                rate_limit_args={'num_requests': 3, 'time_window': 60}
            ))
            self.app.add_handler(CommandHandler(
                "help",
                self.help,
                block=True,
                rate_limit_args={'num_requests': 3, 'time_window': 60}
            ))
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.echo,
                block=True,
                rate_limit_args={'num_requests': 10, 'time_window': 60}
            ))
        except Exception as e:
            print(f"Failed to initialize Telegram bot: {e}")
            raise
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
        """Echo back the message received."""
        try:
            # Validate input length
            if len(update.message.text) > 4096:  # Telegram's message length limit
                await update.message.reply_text("Message too long. Please send a shorter message.")
                return
            
            # Sanitize input for display
            sanitized_text = update.message.text.replace('<', '&lt;').replace('>', '&gt;')
            await update.message.reply_text(f"You said: {sanitized_text}")
        except Exception as e:
            print(f"Error in echo handler: {e}")
            await update.message.reply_text("Sorry, something went wrong. Please try again later.")

    def run(self):
        print("Running bot...")
        self.app.run_polling()

    def stop(self):
        """Stop the bot gracefully."""
        if self.app.running:
            print("Stopping bot...")
            self.app.stop()
            self.app.shutdown()
