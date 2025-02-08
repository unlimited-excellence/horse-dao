import telebot

from services.UsersService import UsersService


class TelegramBotService:
    def __init__(self, token: str, users_service: UsersService):
        self.bot = telebot.TeleBot(token)
        self.users_service = users_service

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            status = self.users_service.create_user(message.from_user.id, 0)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id))
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")


    def run(self):
        self.bot.infinity_polling()