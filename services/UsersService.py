from database.database_worker import DatabaseWorker


class UsersService:
    def __init__(self, databaseWorker: DatabaseWorker):
        self.databaseWorker = databaseWorker
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