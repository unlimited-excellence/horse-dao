import telebot


class TelegramBotService:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            self.bot.send_message(message.from_user.id, "Hello, " + message.from_user.first_name)

    def run(self):
        self.bot.infinity_polling()