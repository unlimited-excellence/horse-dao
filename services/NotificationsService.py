
class NotificationsService:
    def __init__(self, bot):
        self.bot = bot
    
    def send_message(self, userid, message):
        self.bot.send_message(user_id, text=message)
        print(f"NotificationsService - Message \"{message}\" to {userid} was send successfully")