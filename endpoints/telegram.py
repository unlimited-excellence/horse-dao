import telebot
import logging

from time import sleep

from services.UsersService import UsersService
from services.NotificationsService import NotificationsService


class TelegramBotService:
    def __init__(self, bot: telebot.TeleBot, users_service: UsersService, notifications_service: NotificationsService, config : dict):
        self.bot = bot
        self.users_service = users_service
        self.notifications_service = notifications_service
        self.config = config
        #hello AlexJenious why we are writing there, instead of that we can speak by voice chat(this is history don`t delete that)
        #hello Nazar. I dont know why we speak there. Andrij speaks, so dont speak in voice chat

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            status = self.users_service.create_user(str(message.chat.id), 0)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id))
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")

            sleep(int(self.config["giveTokensWhenStartAfterSeconds"]))
            
            users_service.give_tokens(str(message.chat.id), int(self.config["giveTokensWhenStartAmount"]))   
                                      
            self.notifications_service.send_message(str(message.chat.id), "Something going on")

        @self.bot.message_handler(commands=['balance'])
        def handle_balance_message(message):
            user_get_balance = users_service.get_balance(str(message.chat.id))
            if user_get_balance is None:
                self.bot.send_message(message.from_user.id, "Please send /start")
            else:
                self.bot.send_message(message.from_user.id, "Your balance is: " + str(user_get_balance))
        @self.bot.message_handler(commands=['pay'])
        def handle_balance_message(message):
            args = message.text.split(' ')
            try:
                receiver = str(args[1])
                amount = int(args[2])
                if amount <= 0:
                    self.bot.send_message(str(message.from_user.id), "Error: You can`t send negative or zero amount of tokens")
                    return
                if not self.users_service.is_user_registered(receiver):
                    self.bot.send_message(str(message.from_user.id), "Error: the receiver does not exist. Double check receiver\'s user_id")
                    return
                result = self.users_service.transact(str(message.chat.id), receiver, amount)
                if not result:
                    self.bot.send_message(str(message.from_user.id), "Error: insufficient balance")
            except:
                self.bot.send_message(str(message.from_user.id), "Error: invalid arguments. Please call this command in the following format: /pay <to_user_id> <amount>")
            
    def run(self):
        self.bot.infinity_polling()