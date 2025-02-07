import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi

class MongoDbClient:
    def __init__(self):
        print("Initializing database...")
        self.database = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))["horse-project"]