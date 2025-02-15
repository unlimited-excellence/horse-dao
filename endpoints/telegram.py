import telebot

from time import sleep

from services.UsersService import UsersService
from services.NotificationsService import NotificationsService


class TelegramBotService:
    def __init__(self, bot: telebot.TeleBot, users_service: UsersService, notifications_service: NotificationsService):
        self.bot = bot
        self.users_service = users_service
        self.notifications_service = notifications_service

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            status = self.users_service.create_user(message.from_user.id, 0)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id))
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")

            sleep(5)
            
            users_service.give_tokens(message.chat.id, 5)
            self.notifications_service.send_message(message.from_user.id, "Something going on")

        @self.bot.message_handler(commands=['balance'])
        def handle_balance_message(message):
            user_get_balance = users_service.get_balance(message.chat.id)
            if user_get_balance is None:
                self.bot.send_message(message.from_user.id, "Please send /start")
            else:
                self.bot.send_message(message.from_user.id, "Your balance is: " + str(user_get_balance))

    def run(self):
        self.bot.infinity_polling()