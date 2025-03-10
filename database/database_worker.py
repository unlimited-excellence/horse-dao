import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi


class DatabaseWorker:
    def __init__(self, mongodb_uri: str, database_name: str):
        self.client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        self.database = self.client[database_name]
    def insert_one(self, collection: str, document: dict):
        self.database[collection].insert_one(document)
    def find_one(self, collection: str, filter: dict):
        return self.database[collection].find_one(filter)
    def update_one(self, collection: str, filter: dict, update: dict):
        return self.database[collection].update_one(filter, update)
    def find(self, collection: str, filter: dict):
        return self.database[collection].find(filter)