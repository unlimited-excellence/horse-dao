import logging
from typing import Any
from db.mongo_client import MongoDBClient

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервіс для обробки реєстрації користувачів.

    Цей сервіс перевіряє, чи існує користувач з заданим Telegram ID у колекції "users".
    Якщо запис відсутній – створює нового користувача.
    Якщо користувач уже зареєстрований – повертає повідомлення про це.
    """

    def __init__(self, db_client: MongoDBClient) -> None:
        """
        Ініціалізує сервіс з підключенням до MongoDB.

        :param db_client: Екземпляр MongoDBClient, який містить підключення до бази даних.
        """
        self.db_client = db_client
        self.collection = self.db_client.database["users"]

    def register_user(self, telegram_id: int, **user_data: Any) -> str:
        """
        Реєструє користувача за його Telegram ID.

        Перевіряє наявність запису в колекції "users". Якщо користувач уже існує,
        повертає повідомлення "User already registered". Інакше – вставляє новий запис
        і повертає повідомлення "User registered successfully".

        :param telegram_id: Telegram ID користувача.
        :param user_data: Додаткові дані користувача (наприклад, ім'я, нікнейм тощо).
        :return: Результуюче повідомлення про статус реєстрації.
        """
        existing_user = self.collection.find_one({"telegram_id": telegram_id})
        if existing_user:
            logger.info(f"Користувач з Telegram ID {telegram_id} вже зареєстрований.")
            return "User already registered"

        new_user = {"telegram_id": telegram_id, **user_data}
        result = self.collection.insert_one(new_user)
        logger.info(f"Новий користувач зареєстрований з ID {result.inserted_id}")
        return "User registered successfully"
