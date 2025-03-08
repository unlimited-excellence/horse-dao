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
                "giveTokensWhenStartAmount" : 10,
                "codeforces":{
                    "refresh_contests_results_cooldown": 1*24*60*60*1000,
                    "proceed_contests_after": 3*24*60*60*1000,
                    "not_proceed_contests_after": 14*24*60*60*1000
                }
            })
        else:
            return config