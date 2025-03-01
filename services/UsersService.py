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
    def is_user_registered(self, user_id: str) -> bool:
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        })
        if user is None:
            return False
        return True
    def transact(self, from_user : str, to_user : str, amount : int ) -> bool :
        update_one_result = self.databaseWorker.update_one('users', {
            "userId": from_user,
            "balance":{
                "$gte": amount
            }
        }, {
            "$inc":{
                "balance" : -amount
            }
        })
        if update_one_result.modified_count == 0:
            return False
        self.databaseWorker.update_one('users', {
            "userId" : to_user
        }, {
            "$inc": {
                "balance" : amount
            }
        })
        self.notifications_service.send_message(from_user,"You send " + str(amount) + " to " + to_user + ".\n" + "Now your balance is: " + str(self.get_balance(from_user)))  
        self.notifications_service.send_message(to_user, "You received " + str(amount) + ".\n" + "From user " + str(from_user))
        return True
        
        
        # user = self.databaseWorker.find_one('users', {
        #     "userId": user_id
        # })
        # user["balance"] += amount
        # self.databaseWorker.insert_one('users', user)