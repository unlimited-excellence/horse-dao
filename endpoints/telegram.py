import telebot

from time import sleep

from services.UsersService import UsersService
from services.NotificationsService import NotificationsService


class TelegramBotService:
    def __init__(self, bot: telebot.TeleBot, users_service: UsersService, notifications_service: NotificationsService, config : dict):
        self.bot = bot
        self.users_service = users_service
        self.notifications_service = notifications_service
        self.config = config

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            status = self.users_service.create_user(message.from_user.id, 0)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id) )
                self.bot.send.message(message.from_user.id, "\nLink your account to start earning HORSE tokens. To link your account write command /link <codeforce> <your_handle>")
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")

            sleep(int(self.config["giveTokensWhenStartAfterSeconds"]))
            
            users_service.give_tokens(message.chat.id, int(self.config["giveTokensWhenStartAmount"]))   
                                      
            self.notifications_service.send_message(message.from_user.id, "Something going on")

        @self.bot.message_handler(commands=['balance'])
        def handle_balance_message(message):
            user_get_balance = users_service.get_balance(message.chat.id)
            if user_get_balance is None:
                self.bot.send_message(message.from_user.id, "Please send /start")
            else:
                self.bot.send_message(message.from_user.id, "Your balance is: " + str(user_get_balance))

        @self.bot.message_handler(commands=['link'])
        def handle_balance_message(message):
            s=message.text.split()
            user_handle=s[2]
            link_to_connect = s[1].lower()
            supported_sites = ["codeforce", ""]
            try:
            if link_to_connect not in supported_sites:
                self.bot.send_message(message.from_user.id, "Unsupported platform '{link_to_connect}'.\nSupported platforms: {', '.join(supported_sites)}")
                return
            users_service.link_codeforce(user_handle, message.chat.id)
            #має бути ще експет і його нема тому помилка але ми його не робили бо не знаєм правильну архітектуру☺, і треба добавити імпорт реквест бо в нас не працювало
    def run(self):
        self.bot.infinity_polling()