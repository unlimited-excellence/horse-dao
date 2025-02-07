import os
import logging
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDbClient:
    """
    A MongoDB client that establishes a connection using environment variables.

    Required Environment Variables:
      - MONGODB_URI: Connection URI for MongoDB.
      - MONGODB_DATABASE: Name of the database (default: "horse-project").
    """

    def __init__(self) -> None:
        logger.info("Initializing database...")

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
            # Test connection with a ping command
            self.client.admin.command('ping')
            self.database = self.client[db_name]
            logger.info(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            logger.exception("Failed to connect to MongoDB")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Closed MongoDB connection")

    def __enter__(self) -> "MongoDbClient":
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit the runtime context and close the connection."""
        self.close()


# Example usage:
if __name__ == "__main__":
    # Using the client as a context manager ensures the connection is closed
    with MongoDbClient() as db_client:
        # Access the database with db_client.database
        pass
