from bson import ObjectId
from datetime import datetime
from pymongo.cursor import Cursor

def mongo_serializer(doc):
    if doc is None:
        return None

    if isinstance(doc, Cursor):
        return [mongo_serializer(d) for d in doc]

    if isinstance(doc, list):
        return [mongo_serializer(item) for item in doc]
    
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
                serialized[key] = mongo_serializer(value)
            elif isinstance(value, list):
                serialized[key] = mongo_serializer(value)
            else:
                serialized[key] = value
        return serialized
    
    return doc