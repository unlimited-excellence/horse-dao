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
            status = self.users_service.create_user(str(message.chat.id), 0)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id) + "\nLink your account to Codeforces to start earning HORSE tokens for participating in contests. To link your account write command /link codeforces <your_handle>" )
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")

            sleep(int(self.config["giveTokensWhenStartAfterSeconds"]))
            
            users_service.give_tokens(str(message.chat.id), int(self.config["giveTokensWhenStartAmount"]))
                                      
            self.notifications_service.send_message(message.from_user.id, "Something going on")

        @self.bot.message_handler(commands=['balance'])
        def handle_balance_message(message):
            user_get_balance = users_service.get_balance(str(message.chat.id))
            if user_get_balance is None:
                self.bot.send_message(message.from_user.id, "Please send /start")
            else:
                self.bot.send_message(message.from_user.id, "Your balance is: " + str(user_get_balance))

        @self.bot.message_handler(commands=['link'])
        def handle_link_message(message):
            s=message.text.split()
            try:
                platform = s[1].lower()
                user_handle = s[2]
                if platform == "codeforces":
                    result = users_service.link_codeforces(user_handle, str(message.chat.id))
                    if result == users_service.LinkCodeforcesResponse.SUCCESS:
                        self.bot.send_message(message.from_user.id, "Codeforces account is linked. Now you can change your first name back.")
                    elif result == users_service.LinkCodeforcesResponse.ERROR_USER_NOT_FOUND:
                        self.bot.send_message(message.from_user.id, "Error. Codeforces account with this handle not found.")
                    elif result == users_service.LinkCodeforcesResponse.ERROR_INCORRECT_FIRST_NAME:
                        self.bot.send_message(message.from_user.id, f" ️Error. Please set your First Name in English in your Codeforces account to your ID ({message.chat.id}). This will help us identify you correctly. Please note that it may take up to 5 minutes to bot to see changes in your name. You can change your first name back later.")
                else:
                    self.bot.send_message(message.from_user.id, f"Unsupported platform '{platform}'.\nSupported platforms: codeforces")
            except:
                self.bot.send_message(message.from_user.id, "Error. Incorrect command format. Please call this command in the following way: /link codeforces <your_handle>")
    def run(self):
        self.bot.infinity_polling()