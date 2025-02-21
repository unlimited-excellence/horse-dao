import logging

import telebot

class NotificationsService:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
    
    def send_message(self, user_id: str, message: str):
        self.bot.send_message(user_id, text=message)
        logging.debug(f"NotificationsService - Message \"{message}\" to {user_id} was send successfully")