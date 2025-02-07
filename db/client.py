import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi

class MongoDbClient:
    def __init__(self):
    def __init__(self):
        print("Initializing database...")
        # Validate environment variables
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        db_name = os.getenv("MONGODB_DATABASE", "horse-project")
        
        try:
            # Configure connection with retry and pooling
            self.client = MongoClient(
                mongodb_uri,
                server_api=ServerApi('1'),
                retryWrites=True,
                w='majority',
                maxPoolSize=50
            )
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[db_name]
            print(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if hasattr(self, 'client'):
            self.client.close()
            print("Closed MongoDB connection")