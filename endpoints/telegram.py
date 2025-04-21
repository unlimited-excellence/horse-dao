import telebot
import logging

from time import sleep

from services.UsersService import UsersService
from services.NotificationsService import NotificationsService


class TelegramBotService:
    lastRayId = -1
    def __init__(self, bot: telebot.TeleBot, users_service: UsersService, notifications_service: NotificationsService):
        self.bot = bot
        self.users_service = users_service
        self.notifications_service = notifications_service
        #hello AlexJenious why we are writing there, instead of that we can speak by voice chat(this is history don`t delete that)
        #hello Nazar. I dont know why we speak there. Andrij speaks, so dont speak in voice chat

        @self.bot.message_handler(commands=['start'])
        def handle_start_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle_start_message({message})")
            status = self.users_service.create_user(str(message.chat.id), 0, ray_id)
            if status:
                self.bot.send_message(message.from_user.id, "Account was created. Your ID is " + str(message.from_user.id) + "\nLink your account to Codeforces to start earning HORSE tokens for participating in contests. To link your account write command /link codeforces <your_handle> (without brackets)" )
            else:
                self.bot.send_message(message.from_user.id, "Error. You are already registered.")
         
        @self.bot.message_handler(commands=['help'])
        def handle_help_message(message):
            self.bot.send_message(message.from_user.id, f"Your Account ID: {message.from_user.id}" + R"""

Commands:
• /help - get help
• /balance - get your balance
• /pay <to_user_id> <amount> - send tokens to another user
• /link codeforces <your_handle> (without brackets) - link your account to Codeforces to start earning HORSE tokens for participating in contests""")

        @self.bot.message_handler(commands=['balance'])
        def handle_balance_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle_balance_message({message})")
            user_get_balance = users_service.get_balance(str(message.chat.id), ray_id)
            if user_get_balance is None:
                self.bot.send_message(message.from_user.id, "Please send /start")
            else:
                self.bot.send_message(message.from_user.id, "Your balance is: " + str(user_get_balance))

        @self.bot.message_handler(commands=['pay'])
        def handle_pay_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle_pay_message({message})")
            args = message.text.split(' ')
            try:
                receiver = str(args[1])
                amount = float(args[2])
                if amount <= 0:
                    self.bot.send_message(str(message.from_user.id), "Error: You can`t send negative or zero amount of tokens")
                    return
                if not self.users_service.is_user_registered(receiver, ray_id):
                    self.bot.send_message(str(message.from_user.id), "Error: the receiver does not exist. Double check receiver\'s user_id")
                    return
                result = self.users_service.transact(str(message.chat.id), receiver, amount, ray_id)
                if not result:
                    self.bot.send_message(str(message.from_user.id), "Error: insufficient balance")
            except:
                self.bot.send_message(str(message.from_user.id), "Error: invalid arguments. Please call this command in the following format: /pay <to_user_id> <amount>")

        @self.bot.message_handler(commands=['link'])
        def handle_link_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle_link_message({message})")
            s=message.text.split()
            try:
                platform = s[1].lower()
                user_handle = s[2]
                if user_handle[0] == '<' or user_handle[-1] == '>':
                    raise ValueError("Handle should not contain '<' or '>'")
                if platform == "codeforces":
                    result = users_service.link_codeforces(user_handle, str(message.chat.id), ray_id)
                    if result == users_service.LinkCodeforcesResponse.SUCCESS:
                        self.bot.send_message(message.from_user.id, "Codeforces account is linked. Now you can change your first name back.")
                    elif result == users_service.LinkCodeforcesResponse.ERROR_USER_NOT_FOUND:
                        self.bot.send_message(message.from_user.id, "Error. Codeforces account with this handle not found.")
                    elif result == users_service.LinkCodeforcesResponse.ERROR_INCORRECT_FIRST_NAME:
                        self.bot.send_message(message.from_user.id, f" ️Please set your First Name in English in your Codeforces account to your ID ({message.chat.id}). This will help us identify you correctly. Then enter the same command. Please note that it may take up to 5 minutes to bot to see changes in your name. You can change your first name back later.")
                    elif result == users_service.LinkCodeforcesResponse.ERROR_ALREADY_USED_ACCOUNT:
                        self.bot.send_message(message.from_user.id, f" ️Error. Account {user_handle} is already linked. Account on Codeforces can be linked only to one person.")
                else:
                    self.bot.send_message(message.from_user.id, f"Error. Unsupported platform '{platform}'.\nSupported platforms: codeforces")
            except Exception as e:
                self.bot.send_message(message.from_user.id, "Error. Incorrect command format. Please call this command in the following way: /link codeforces <your_handle> (without brackets)")
                logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - Error. Possibly incorrect input - {e}")

        @self.bot.message_handler(commands=['_give'])
        def handle__give_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle__give_message({message})")
            try:
                if not self.users_service.is_user_admin(str(message.from_user.id), ray_id):
                    self.bot.send_message(message.from_user.id, f"Error. This command is only for admins.")
                else:
                    s = message.text.split()
                    receiver_id = s[1]
                    amount = float(s[2])
                    message_text = None
                    if len(s) > 3:
                       message_text = " ".join(s[3:])
                    self.users_service.give_tokens(receiver_id, amount, message_text, ray_id)
            except Exception as e:
                self.bot.send_message(message.from_user.id, "Error. Incorrect command format. Please call this command in the following way: /_give <user_id> <amount> <message>")
                logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - Error. Possibly incorrect input - {e}")

        @self.bot.message_handler(commands=['_announce'])
        def handle__announce_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle__announce_message({message})")
            try:
                if not self.users_service.is_user_admin(str(message.from_user.id), ray_id):
                    self.bot.send_message(message.from_user.id, f"Error. This command is only for admins.")
                else:
                    s = message.text.split()
                    message_text = " ".join(s[1:])
                    if message_text == "":
                        raise ValueError("Message should not be empty")
                    self.users_service.announce(message_text, ray_id)
            except Exception as e:
                self.bot.send_message(message.from_user.id, "Error. Incorrect command format. Please call this command in the following way: /_announce <message>")
                logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - Error. Possibly incorrect input - {e}")

        @self.bot.message_handler(commands=['_test_announce', '_testnounce'])
        def handle__test_announce_message(message):
            self.lastRayId += 1; ray_id = self.lastRayId
            logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - handle__test_announce_message({message})")
            try:
                if not self.users_service.is_user_admin(str(message.from_user.id), ray_id):
                    self.bot.send_message(message.from_user.id, f"Error. This command is only for admins.")
                else:
                    s = message.text.split()
                    message_text = " ".join(s[1:])
                    if message_text == "":
                        raise ValueError("Message should not be empty")
                    self.users_service.test_announce(str(message.from_user.id), message_text, ray_id)
            except Exception as e:
                self.bot.send_message(message.from_user.id, "Error. Incorrect command format. Please call this command in the following way: /_test_announce <message>")
                logging.debug(f"TELEGRAM_BOT_SERVICE: {ray_id} - Error. Possibly incorrect input - {e}")

    def run(self):
        self.bot.infinity_polling()