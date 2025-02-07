import os
import sys
import signal
import logging

from db.mongo_client import MongoDBClient
from bot.telegram_bot import TelegramBot
from services.user_services import UserService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    try:
        # Initialize the database and bot clients
        db_client = MongoDBClient()
        user_service = UserService(db_client)
        bot = TelegramBot(user_service)

        # Define a shutdown handler to gracefully close resources.
        def shutdown(signum, frame):
            logger.info("Received shutdown signal. Shutting down...")
            try:
                bot.stop()  # Make sure TelegramBot.stop() is implemented
                db_client.close()  # Make sure MongoDbClient.close() is implemented
            except Exception as e:
                logger.exception("Error during shutdown")
            sys.exit(0)

        # Register shutdown signals
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        # Run the bot (this is a blocking call)
        bot.run()

    except Exception as e:
        logger.exception("Error during bot initialization or runtime")
        sys.exit(1)


if __name__ == '__main__':
    main()
