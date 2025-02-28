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
    def link_codeforce(self, handle: str, user_id: str) -> str:
        self.handle=handle
        self.user_id=user_id
        #response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}&checkHistoricHandles=false")
        #response_dict = response.json()
        #self.codeforce_firstName = response_dict["result"][0].get("firstName", "No First Name")
        if user_id is #codeforce_firstName :
            self.databaseWorker.update_one('users',{
            "userId": user_id
            }, {
                "$setOnInsert": {
                    "codeforce": {
                        "codeforce_handle": handle
                    }
                }
            })
            self.notifications_service.send_message(user_id, "Codeforce account is linked.")
        else:
            self.notifications_service.send_message(user_id, " ️Please set your First Name in your Codeforces account to your ID. This will help us identify you correctly.")



        #42bratuha
        # user = self.databaseWorker.find_one('users', {
        #     "userId": user_id
        # })
        # user["balance"] += amount
        # self.databaseWorker.insert_one('users', user)