from pymongo import MongoClient
from time import sleep

from ..core.config import *
from ..core.logger import *


class Database:
    def __init__(self):
        # Initialize the MongoDB client and Database
        self.client = None
        self.db = None
        # Attempt to connect with 3 retries
        for attempt in range(3):
            try:
                self.connect()
                break
            except Exception as e:
                log_error(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    log_error("Failed to connect to MongoDB after 3 attempts.")
                    raise
                log_warning(f"Retrying MongoDB connection in 5 seconds...")
                sleep(5)

    def connect(self):
        self.client = MongoClient(MONGO_URI())
        # Use ismaster command
        self.client.admin.command("ismaster")
        self.db = self.client[DATABASE_NAME()]
        log_info("Successfully connected to MongoDB")

    def get_collection(self, collection_name):
        if self.client is not None and self.db is not None:
            return self.db[collection_name]
        else:
            log_error("Database connection is not established")
            return None

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            log_info("MongoDB connection closed")
        else:
            log_error("MongoDB client is not initialized")


database = Database()
