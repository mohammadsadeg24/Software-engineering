from mongodb_connector import mongodb
from bson import ObjectId
from django.utils.text import slugify

def get_object_id(id_string):
    try:
        return ObjectId(id_string)
    except:
        return None

def generate_unique_slug(collection, title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while mongodb.database[collection].find_one({"slug": slug}):
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

def cart_total_amount(cart):
    total_amount = 0
    for item in cart['items']:
        product_slug = item['product_slug']
        product_price = mongodb.database['products'].find_one({"slug":product_slug})['price']
        total_amount += item['quantity'] * product_price

    return total_amount