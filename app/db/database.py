from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ..core.config import settings
from ..utils.logger import *


class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(settings.MONGO_URI)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command("ismaster")
            self.db = self.client[settings.DATABASE_NAME]
            log_info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            log_error(f"Could not connect to MongoDB: {e}")
            raise

    def get_collection(self, collection_name):
        if self.db is not None:
            return self.db[collection_name]
        else:
            log_error("Database connection is not established")
            return None

    def close(self):
        if self.client is not None:
            self.client.close()
            log_info("MongoDB connection closed")


database = Database()
