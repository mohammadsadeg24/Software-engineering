from bson import ObjectId
from datetime import datetime
from pymongo.cursor import Cursor
from mongodb_connector import mongodb

from core.models import User
from honey_api.utils import get_object_id

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
                serialized[key] = value
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
    cart['cart_id'] = cart['_id']
    cart['shipping'] = 6
    cart['tax'] = 5
    cart['total'] = cart['subtotal'] + cart['shipping'] + cart['tax']
    return context

def review_serializer(reviews):
    context = []

    for review in reviews:
        username = User.objects.get(id=review['user_id'])
        rev = {
            'username': username,
            'rating': review['rating'],
            'comment': review['comment'],
            'date': review['date'],
        }
        context.append(rev)

    return context

def product_serializer(product):
    context = mongo_serializer(product)

    category_id = get_object_id(product['category_id'])
    category = mongodb.database['categories'].find_one({'_id':category_id})
    
    context['category_slug'] = category['slug']
    context['category_name'] = category['name']

    return context

def order_serializer(orders):
    orders = mongo_serializer(orders)
    total_spend = 0

    for order_index in range(len(orders)):
        order_data = []
           
        total_spend += orders[order_index]['total_amount']

        for item in orders[order_index]['items']:
            product = mongodb.database['products'].find_one({'slug': item['product_slug']})
            data = {
                'name': product['title'],
                'quantity': item['quantity'],
                'price': product['price'],
                'total_amount': product['price'] * item['quantity'],
            }
            order_data.append(data)

        orders[order_index]['items'] = order_data

    return total_spend, orders