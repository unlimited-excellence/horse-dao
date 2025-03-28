import logging
import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi


class DatabaseWorker:
    lastRayId = 0
    def __init__(self, mongodb_uri: str, database_name: str):
        self.client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        self.database = self.client[database_name]
    def insert_one(self, collection: str, document: dict, ray_id: int = -1):
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - called insert_one({collection}, {document})")
        self.database[collection].insert_one(document)
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - success")
    def find_one(self, collection: str, filter: dict, ray_id: int = -1):
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - called find_one({collection}, {filter})")
        result = self.database[collection].find_one(filter)
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - success with result {result}")
        return result
    def update_one(self, collection: str, filter: dict, update: dict, ray_id: int = -1):
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - called update_one({collection}, {filter}, {update})")
        result = self.database[collection].update_one(filter, update)
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - success with result {result}")
        return result
    def find(self, collection: str, filter: dict, ray_id: int = -1):
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - called find({collection}, {filter})")
        result = self.database[collection].find(filter)
        logging.debug("DATABASE_WORKER: " + f"{ray_id} - success with result {result}")
        return result