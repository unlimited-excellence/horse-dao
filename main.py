import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi

if __name__ == '__main__':
    print("Initializing database...")
    database = MongoClient(os.getenv("MONGODB_URI"), server_api=ServerApi('1'))["horse-project"]

    # Changed nothing