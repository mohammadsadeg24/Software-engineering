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