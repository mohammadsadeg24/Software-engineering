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
            mongo_settings = settings.MONGODB_SETTINGS
            
            # Use the complete connection string from the host key
            connection_string = mongo_settings['host']
            
            # Connect using the full string
            self._client = MongoClient(connection_string)
            
            # Get the database. Use the explicitly set name from settings if available,
            # otherwise it will use the one from the connection string.
            db_name = mongo_settings.get('db', None)
            self._database = self._client[db_name] if db_name else self._client.get_database()
            
            # Verify connection
            self._client.admin.command('ismaster')
            logger.info("MongoDB connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @property
    def database(self):
        if self._database is not None:
            self.connect()
        return self._database

mongodb = MongoDBConnection()