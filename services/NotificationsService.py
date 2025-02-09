
class NotificationsService:
    def __init__(self, telegram_bot_service):
        self.telegram_bot_service = telegram_bot_service
    
    def send_message(self, userid, message):
        self.telegram_bot_service.bot.send_message(userid, text=message)
        print(f"NotificationsService - Message \"{message}\" to {userid} was send successfully")