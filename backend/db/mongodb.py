# db/mongodb.py
from pymongo import MongoClient, ASCENDING, DESCENDING
from django.conf import settings
from bson import ObjectId
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
    
    def connect(self):
        try:
            mongo_settings = settings.MONGODB_SETTINGS
            
            if mongo_settings['username'] and mongo_settings['password']:
                connection_string = f"mongodb://{mongo_settings['username']}:{mongo_settings['password']}@{mongo_settings['host']}:{mongo_settings['port']}/{mongo_settings['db_name']}"
            else:
                connection_string = f"mongodb://{mongo_settings['host']}:{mongo_settings['port']}"
            
            self._client = MongoClient(connection_string)
            self._database = self._client[mongo_settings['db_name']]
            
            # Test connection
            self._client.admin.command('ismaster')
            logger.info("MongoDB connection established successfully")
            
            # Create indexes
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for better performance"""
        try:
            # Products indexes
            self._database.products.create_index([("slug", ASCENDING)], unique=True)
            self._database.products.create_index([("category_id", ASCENDING)])
            self._database.products.create_index([("title", "text"), ("description", "text")])
            
            # Categories indexes
            self._database.categories.create_index([("slug", ASCENDING)], unique=True)
            self._database.categories.create_index([("parent_id", ASCENDING)])
            
            # Orders indexes
            self._database.orders.create_index([("user_id", ASCENDING)])
            self._database.orders.create_index([("created_at", DESCENDING)])
            
            # Reviews indexes
            self._database.reviews.create_index([("product_id", ASCENDING)])
            self._database.reviews.create_index([("user_id", ASCENDING)])
            
            # Cart indexes
            self._database.carts.create_index([("user_id", ASCENDING)], unique=True)
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    @property
    def database(self):
        if self._database is None:
            self.connect()
        return self._database
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._database = None

# Singleton instance
mongodb = MongoDBConnection()

# Helper functions
def get_object_id(id_string):
    """Convert string to ObjectId, return None if invalid"""
    try:
        return ObjectId(id_string)
    except:
        return None

def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_mongo_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == '_id':
                serialized['id'] = str(value)
            elif isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = serialize_mongo_doc(value)
            elif isinstance(value, list):
                serialized[key] = serialize_mongo_doc(value)
            else:
                serialized[key] = value
        return serialized
    
    return doc