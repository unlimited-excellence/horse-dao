import logging
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
            logging.debug(f"MISC_SERVICE: Config is missing, creating a new one...")
            config = {
                "type": "config",
                "createdAt": datetime.now(),
                "telegram": {
                    "BOT_TOKEN": "<TOKEN>"
                },
                "codeforces": {
                    "refresh_contests_results_cooldown": 1*24*60*60*1000,
                    "proceed_contests_after": 3*24*60*60*1000,
                    "not_proceed_contests_after": 14*24*60*60*1000,
                    "APIKey": "<KEY>",
                    "APISecret": "<SECRET>"
                }
            }
            self.databaseWorker.insert_one('misc', config)
            logging.debug(f"MISC_SERVICE: A new config was created: {config}")

        logging.debug(f"MISC_SERVICE: Config is {config}")
        return config