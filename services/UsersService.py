from database.database_worker import DatabaseWorker
from services.NotificationsService import NotificationsService

class UsersService:
    def __init__(self, databaseWorker: DatabaseWorker, notifications_service: NotificationsService):
        self.databaseWorker = databaseWorker
        self.notifications_service = notifications_service
    def create_user(self, user_id: str, balance: int) -> bool:
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        })
        if user is None:
            self.databaseWorker.insert_one('users', {
                "userId": user_id,
                "balance": balance
            })
            return True
        else:
            return False
    def get_balance(self, user_id: str) -> int | None:
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        })
        if user is None:
            return None
        else:
            return user["balance"]
    def give_tokens(self, user_id: str, amount: int):
        self.databaseWorker.update_one('users', {
            "userId": user_id
        }, {
            "$inc": {
                "balance": amount
            }
        })
        self.notifications_service.send_message(user_id, "Balance have changed by "+ str(amount) + ".\n" + "Your final balance is " + str(self.get_balance(user_id)))
        
        #42bratuha
        # user = self.databaseWorker.find_one('users', {
        #     "userId": user_id
        # })
        # user["balance"] += amount
        # self.databaseWorker.insert_one('users', user)