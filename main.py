if __name__ == '__main__':
    try:
        db_client = MongoDbClient()
        bot = TelegramBot()
        # Register shutdown handler
        import signal
        def shutdown(signum, frame):
            print("Shutting down...")
            bot.stop()  # Add stop method to TelegramBot
            # Close database connection
            db_client.close()  # Add close method to MongoDbClient
            exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        bot.run()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)