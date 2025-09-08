from mongodb_connector import mongodb
from datetime import datetime

from honey_api.utils import get_object_id, generate_unique_slug, generate_order_number

class BaseMongoModel:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = mongodb.database[collection_name]
    
    def create(self, data):
        self.collection.insert_one(data)

class CategoryManager(BaseMongoModel):
    def __init__(self):
        super().__init__('categories')
    
    def create_category(self, name, description="", parent_id=None):
        data = {
            'name': name,
            'slug': generate_unique_slug(self.collection_name, name),
            'description': description,
            'parent_id': get_object_id(parent_id) if parent_id else None
        }
        self.create(data)
    
    
class ProductManager(BaseMongoModel):
    def __init__(self):
        super().__init__('products')
    
    def create_product(self, title, category_id, price, description):
        data = {
            'title': title,
            'slug': generate_unique_slug(self.collection_name, title),
            'category_id': get_object_id(category_id),
            'price': float(price),
            'description': description,
            'images': [],
            'status': 'active',
            'modified_at': datetime.now()
        }
        self.create(data)
    

class ReviewManager(BaseMongoModel):
    def __init__(self):
        super().__init__('reviews')
    
    def create_review(self, user_id, product_slug, rating, comment):
        data = {
            'user_id': int(user_id),  
            'product_slug': product_slug,
            'rating': int(rating),
            'comment': comment,
            'date': datetime.now()
        }
        self.create(data)
    

class CartManager(BaseMongoModel):
    def __init__(self):
        super().__init__('carts')
    
    def create_cart(self, user_id):
        cart_data = {
            'user_id': int(user_id),
            'items': [],
            'total_amount': 0.0
        }
        self.create(cart_data)
    

class OrderManager(BaseMongoModel):
    def __init__(self):
        super().__init__('orders')
    
    def create_order(self, user_id, items, total_amount, address_id):
        data = {
            'user_id': int(user_id),
            'items': items,
            'total_amount': float(total_amount),
            'payment_status': 'pending',
            'order_status': 'processing',
            'address_id': address_id,
            'order_number': generate_order_number(),
            'date': datetime.now()
        }
        return self.create(data)
    

categories = CategoryManager()
products = ProductManager()
reviews = ReviewManager()
carts = CartManager()
orders = OrderManager()