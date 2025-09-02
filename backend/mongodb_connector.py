from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    # def connect(self):
    #     try:
    #         mongo_settings = settings.MONGODB_SETTINGS
            
    #         if mongo_settings['username'] and mongo_settings['password']:
    #             connection_string = f"mongodb://{mongo_settings['username']}:{mongo_settings['password']}@{mongo_settings['host']}:{mongo_settings['port']}/{mongo_settings['db_name']}"
    #         else:
    #             connection_string = f"mongodb://{mongo_settings['host']}:{mongo_settings['port']}"
            
    #         self._client = MongoClient(connection_string)
    #         self._database = self._client[mongo_settings['db_name']]
    #         self._client.admin.command('ismaster')
    #         logger.info("MongoDB connection established successfully")
    def connect(self):
        try:
            # Get MongoDB settings
            mongo_settings = settings.MONGODB_SETTINGS
            
            # Connect to MongoDB
            self._client = MongoClient(
                mongo_settings['host'],
                serverSelectionTimeoutMS=5000
            )
            
            # Get the database
            db_name = mongo_settings['db']
            self._database = self._client[db_name]
            
            # Test the connection
            self._client.server_info()
            logger.info(f"MongoDB connection established successfully to {mongo_settings['host']}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    @property
    def database(self):
        if self._database is None:
            self.connect()
        return self._database

mongodb = MongoDBConnection()