import logging
from typing import Any
from db.mongo_client import MongoDBClient

logger = logging.getLogger(__name__)

class UserService:
    """
    Service for handling user registration.

    This service checks if a user with the given Telegram ID exists in the "users" collection.
    If the record does not exist, it creates a new user.
    If the user is already registered, it returns a message indicating so.
    """

    def __init__(self, db_client: MongoDBClient) -> None:
        """
        Initializes the service with a MongoDB connection.

        :param db_client: An instance of MongoDBClient that holds the database connection.
        """
        self.db_client = db_client
        self.collection = self.db_client.database["users"]

    def register_user(self, telegram_id: int, **user_data: Any) -> str:
        """
        Registers a user by their Telegram ID.

        Checks the "users" collection for an existing record. If the user already exists,
        returns the message "User already registered". Otherwise, inserts a new record
        and returns the message "User registered successfully".

        :param telegram_id: The user's Telegram ID.
        :param user_data: Additional user data (e.g., first name, username, last name, etc.).
        :return: A message indicating the registration status.
        """
        existing_user = self.collection.find_one({"telegram_id": telegram_id})
        if existing_user:
            logger.info(f"User with Telegram ID {telegram_id} is already registered.")
            return "User already registered"

        new_user = {"telegram_id": telegram_id, **user_data}
        result = self.collection.insert_one(new_user)
        logger.info(f"New user registered with ID {result.inserted_id}")
        return "User registered successfully"
