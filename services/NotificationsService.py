import logging

import telebot

class NotificationsService:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
    
    def send_message(self, user_id: str, message: str, ray_id: int = -1, markdown: bool = False):
        try:
            logging.debug(f"NOTIFICATIONS_SERVICE: {ray_id} - Sending message \"{message}\" to {user_id}...")
            self.bot.send_message(user_id, text=(message.replace("\\n", "\n").replace("!", "\!").replace(".", "\.").replace("-", "\-").replace("\\\\", "\\") if markdown else message), parse_mode=("MarkdownV2" if markdown else None))
            logging.debug(f"NOTIFICATIONS_SERVICE: {ray_id} - Message was sent successfully")
        except Exception as e:
            logging.error(f"NOTIFICATIONS_SERVICE: {ray_id} - Message was not sent due to error: {e}")