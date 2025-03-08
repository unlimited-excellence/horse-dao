import logging
from enum import EnumMeta, Enum

import requests

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
    def give_tokens(self, user_id: str, amount: int, message: str | None = None):
        self.databaseWorker.update_one('users', {
            "userId": user_id
        }, {
            "$inc": {
                "balance": amount
            }
        })

        if message is None:
            message = "Balance have changed by "+ str(amount) + ".\n" + "Your final balance is " + str(self.get_balance(user_id))
        
        self.notifications_service.send_message(user_id, message)

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

    class LinkCodeforcesResponse(Enum):
        SUCCESS = 0
        ERROR_USER_NOT_FOUND = 1
        ERROR_INCORRECT_FIRST_NAME = 2

    def link_codeforces(self, handle: str, user_id: str) -> LinkCodeforcesResponse:
        response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}&checkHistoricHandles=false")
        response_dict = response.json()
        if response_dict['status'] != "OK":
            return self.LinkCodeforcesResponse.ERROR_USER_NOT_FOUND
        codeforces_first_name = response_dict["result"][0].get("firstName", None)
        if user_id == codeforces_first_name:
            self.databaseWorker.update_one('users',{
                "userId": user_id
            }, {
                "$set": {
                    "codeforces": {
                        "handle": handle
                    }
                }
            })
            return self.LinkCodeforcesResponse.SUCCESS
        else:
            logging.debug(f"User {user_id} tried to link Codeforces account with handle {handle} but first name in Codeforces account is {codeforces_first_name}")
            return self.LinkCodeforcesResponse.ERROR_INCORRECT_FIRST_NAME
        #42bratuha

