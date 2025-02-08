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