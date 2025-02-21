from datetime import datetime

from database.database_worker import DatabaseWorker


class MiscService:
    def __init__(self, databaseWorker: DatabaseWorker):
        self.databaseWorker = databaseWorker
    def get_or_create_config(self) -> dict:
        config = self.databaseWorker.find_one('misc', {
            "type" : "config"
        })
        if config is None:
            self.databaseWorker.insert_one('misc', {
                "type": "config",
                "createdAt": datetime.now(),
                "giveTokensWhenStartAfterSeconds" : 5,
                "giveTokensWhenStartAmount" : 10
            })
        else:
            return config