from mongodb_connector import mongodb
from django.utils.text import slugify
from datetime import datetime
import uuid

from honey_api.utils import get_object_id, generate_unique_slug
from honey_api.serializer import mongo_serializer

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
            'slug': generate_unique_slug(name),
            'description': description,
            'parent_id': get_object_id(parent_id) if parent_id else None
        }
        self.create(data)
    
    
class ProductManager(BaseMongoModel):
    def __init__(self):
        super().__init__('products')
    
    def create_product(self, title, category_id, price, description="", variants=None):
        data = {
            'title': title,
            'slug': generate_unique_slug(title),
            'category_id': get_object_id(category_id),
            'price': float(price),
            'description': description,
            'variants': variants or [],
            'images': [],
            'status': 'active',
            'modified_at': datetime.now()
        }
        self.create(data)
    

class ReviewManager(BaseMongoModel):
    def __init__(self):
        super().__init__('reviews')
    
    def create_review(self, user_id, product_id, rating, comment=""):
        """Create a new review"""
        # Check if user already reviewed this product
        existing = self.collection.find_one({
            "user_id": int(user_id),
            "product_id": get_object_id(product_id)
        })
        
        if existing:
            raise ValueError("User has already reviewed this product")
        
        data = {
            'user_id': int(user_id),  
            'product_id': get_object_id(product_id),
            'rating': int(rating),
            'comment': comment,
            'date': datetime.now()
        }
        elf.create(data)
    
    def get_product_reviews(self, product_id, limit=20, skip=0):
        """Get reviews for a product"""
        return self.find_all(
            {"product_id": get_object_id(product_id)},
            limit=limit,
            skip=skip,
            sort=[("date", -1)]
        )
    
    def get_product_rating_summary(self, product_id):
        """Get rating summary for a product"""
        pipeline = [
            {"$match": {"product_id": get_object_id(product_id)}},
            {"$group": {
                "_id": None,
                "average_rating": {"$avg": "$rating"},
                "total_reviews": {"$sum": 1},
                "rating_counts": {
                    "$push": "$rating"
                }
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {"average_rating": 0, "total_reviews": 0}
        
        summary = result[0]
        rating_distribution = {}
        for rating in summary.get('rating_counts', []):
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        return {
            "average_rating": round(summary.get('average_rating', 0), 2),
            "total_reviews": summary.get('total_reviews', 0),
            "rating_distribution": rating_distribution
        }

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
    
    def create_order(self, user_id, items, total_amount, address_data=None, description=""):
        """Create a new order"""
        data = {
            'user_id': int(user_id),
            'items': items,
            'total_amount': float(total_amount),
            'payment_status': 'pending',
            'order_status': 'processing',
            'description': description,
            'address': address_data,
            'order_number': self._generate_order_number()
        }
        return self.create(data)
    
    def _generate_order_number(self):
        """Generate unique order number"""
        return f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

    def get_user_orders(self, user_id, limit=20, skip=0):
        """Get orders for a user"""
        return self.find_all(
            {"user_id": int(user_id)},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]
        )
    
    def update_payment_status(self, order_id, status, transaction_ref=""):
        """Update order payment status"""
        update_data = {
            'payment_status': status,
            'transaction_ref': transaction_ref
        }
        return self.update_by_id(order_id, update_data)

categories = CategoryManager()
products = ProductManager()
reviews = ReviewManager()
carts = CartManager()
orders = OrderManager()