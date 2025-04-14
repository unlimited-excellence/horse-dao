import logging
from enum import EnumMeta, Enum

import requests

from database.database_worker import DatabaseWorker
from services.NotificationsService import NotificationsService

class UsersService:
    def __init__(self, databaseWorker: DatabaseWorker, notifications_service: NotificationsService):
        self.databaseWorker = databaseWorker
        self.notifications_service = notifications_service
    def create_user(self, user_id: str, balance: float, ray_id: int = -1) -> bool:
        logging.debug(f"USERS_SERVICE: {ray_id} - create_user({user_id}, {balance})")
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        }, ray_id)
        if user is None:
            self.databaseWorker.insert_one('users', {
                "userId": user_id,
                "balance": balance
            }, ray_id)
            logging.debug(f"USERS_SERVICE: {ray_id} - response=True")
            return True
        else:
            logging.debug(f"USERS_SERVICE: {ray_id} - response=False")
            return False
    def get_balance(self, user_id: str, ray_id: int = -1) -> float | None:
        logging.debug(f"USERS_SERVICE: {ray_id} - get_balance({user_id})")
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        }, ray_id)
        if user is None:
            logging.debug(f"USERS_SERVICE: {ray_id} - response=None")
            return None
        else:
            logging.debug(f"USERS_SERVICE: {ray_id} - response={user["balance"]}")
            return user["balance"]
    def give_tokens(self, user_id: str, amount: float, message: str | None = None, ray_id: int = -1):
        logging.debug(f"USERS_SERVICE: {ray_id} - give_tokens({user_id}, {amount}, {message})")
        self.databaseWorker.update_one('users', {
            "userId": user_id
        }, {
            "$inc": {
                "balance": amount
            }
        }, ray_id)

        user_balance = str(self.get_balance(user_id, ray_id))
        if message is None:
            message = "Balance have changed by "+ str(amount) + ".\n" + f"Your final balance is {user_balance}"

        logging.debug(f"USERS_SERVICE: {ray_id} - Successfully given tokens")
        self.notifications_service.send_message(user_id, message.replace("%AMOUNT%", str(amount)).replace("%BALANCE%", user_balance), ray_id)

    def is_user_registered(self, user_id: str, ray_id: int = -1) -> bool:
        logging.debug(f"USERS_SERVICE: {ray_id} - is_user_registered({user_id})")
        user = self.databaseWorker.find_one('users', {
            "userId": user_id
        }, ray_id)
        if user is None:
            logging.debug(f"USERS_SERVICE: {ray_id} - response=False")
            return False
        logging.debug(f"USERS_SERVICE: {ray_id} - response=True")
        return True

    def is_user_admin(self, user_id: str, ray_id: int = -1) -> bool:
        logging.debug(f"USERS_SERVICE: {ray_id} - is_user_admin({user_id})")
        user = self.databaseWorker.find_one('rbac-users-roles', {
            'userId': user_id,
            'role': 'admin'
        })
        logging.debug(f"USERS_SERVICE: {ray_id} - response={user is not None}")
        return user is not None

    def announce(self, message: str, ray_id: int = -1):
        logging.debug(f"USERS_SERVICE: {ray_id} - announce({message})")
        users = self.databaseWorker.find('users', {}, ray_id)
        for user in users:
            codeforces_handle = user.get("codeforces", {}).get("handle", "\[codeforces handle is not specified\]")
            self.notifications_service.send_message(user["userId"], message.replace("%USER_ID%", user["userId"]).replace("%CODEFORCES_HANDLE%", codeforces_handle), ray_id, markdown=True)
        logging.debug(f"USERS_SERVICE: {ray_id} - response=success")

    def test_announce(self, receiver_id: str, message: str, ray_id: int = -1):
        logging.debug(f"USERS_SERVICE: {ray_id} - test_announce({receiver_id}, {message})")
        user = self.databaseWorker.find_one('users', {
            "userId": receiver_id
        }, ray_id)
        codeforces_handle = user.get("codeforces", {}).get("handle", "\[codeforces handle is not specified\]")
        self.notifications_service.send_message(user["userId"], message.replace("%USER_ID%", user["userId"]).replace("%CODEFORCES_HANDLE%", codeforces_handle), ray_id, markdown=True)
        logging.debug(f"USERS_SERVICE: {ray_id} - response=success")

    def transact(self, from_user: str, to_user: str, amount: float, ray_id: int = -1) -> bool :
        logging.debug(f"USERS_SERVICE: {ray_id} - transact({from_user}, {to_user}, {amount})")
        update_one_result = self.databaseWorker.update_one('users', {
            "userId": from_user,
            "balance":{
                "$gte": amount
            }
        }, {
            "$inc":{
                "balance" : -amount
            }
        }, ray_id)
        if update_one_result.modified_count == 0:
            logging.debug(f"USERS_SERVICE: {ray_id} - response=False")
            return False
        self.databaseWorker.update_one('users', {
            "userId" : to_user
        }, {
            "$inc": {
                "balance" : amount
            }
        }, ray_id)
        self.notifications_service.send_message(from_user,"You have sent " + str(amount) + " to user " + to_user + ".\n" + "Now your balance is: " + str(self.get_balance(from_user, ray_id)), ray_id)
        self.notifications_service.send_message(to_user, "You received " + str(amount) + " from user " + str(from_user), ray_id)
        logging.debug(f"USERS_SERVICE: {ray_id} - response=True")
        return True

    class LinkCodeforcesResponse(Enum):
        SUCCESS = 0
        ERROR_USER_NOT_FOUND = 1
        ERROR_INCORRECT_FIRST_NAME = 2
        ERROR_ALREADY_USED_ACCOUNT = 3

    def link_codeforces(self, handle: str, user_id: str, ray_id: int = -1) -> LinkCodeforcesResponse:
        logging.debug(f"USERS_SERVICE: {ray_id} - link_codeforces({handle}, {user_id})")
        response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}&checkHistoricHandles=false")
        response_dict = response.json()
        if response_dict['status'] != "OK":
            logging.debug(f"USERS_SERVICE: {ray_id} - response={self.LinkCodeforcesResponse.ERROR_USER_NOT_FOUND.name}")
            return self.LinkCodeforcesResponse.ERROR_USER_NOT_FOUND
        is_registered = self.databaseWorker.find_one('users', {
            "codeforce.handle" : handle
        }, ray_id)
        if is_registered is not None:
            return self.LinkCodeforcesResponse.ERROR_ALREADY_USED_ACCOUNT
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
            }, ray_id)
            logging.debug(f"USERS_SERVICE: {ray_id} - response={self.LinkCodeforcesResponse.SUCCESS.name}")
            return self.LinkCodeforcesResponse.SUCCESS
        else:
            logging.debug(f"USERS_SERVICE: {ray_id} - Error: User {user_id} tried to link Codeforces account with handle {handle} but first name in Codeforces account is {codeforces_first_name}")
            logging.debug(f"USERS_SERVICE: {ray_id} - response={self.LinkCodeforcesResponse.ERROR_INCORRECT_FIRST_NAME.name}")
            return self.LinkCodeforcesResponse.ERROR_INCORRECT_FIRST_NAME
        #42bratuha