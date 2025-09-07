from bson import ObjectId
from datetime import datetime
from pymongo.cursor import Cursor
from mongodb_connector import mongodb

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

def cart_serializer(cart):
    context = cart
    items = [] 
    cart['subtotal'] = 0
    
    for item in cart['items']:
        product = mongodb.database['products'].find_one({"slug": item['product_slug']})
        item_data = {
            'title': product['title'], 
            'slug': product['slug'], 
            'price': product['price'], 
            'quantity': item['quantity'], 
            'total_amount': item['quantity'] * product['price'] 
        }
        cart['subtotal'] = item_data['total_amount']
        items.append(item_data)
    
    cart['items'] = items
    cart['shipping'] = 6
    cart['tax'] = 5
    cart['total'] = cart['subtotal'] + cart['shipping'] + cart['tax']

    return context