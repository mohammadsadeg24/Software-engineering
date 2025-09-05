from mongodb_connector import mongodb
from django.utils.text import slugify
from datetime import datetime
import uuid

from honey_api.utils import get_object_id
from honey_api.serializer import mongo_serializer

class BaseMongoModel:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = mongodb.database[collection_name]
    
    def create(self, data):
        """Create a new document"""
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)
    
    def find_by_id(self, doc_id):
        """Find document by ID"""
        return mongo_serializer(
            self.collection.find_one({"_id": get_object_id(doc_id)})
        )
    
    def find_all(self, filter_dict=None, limit=100, skip=0, sort=None):
        """Find multiple documents"""
        filter_dict = filter_dict or {}
        cursor = self.collection.find(filter_dict)
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(limit)
        return mongo_serializer(list(cursor))
    
    def update_by_id(self, doc_id, update_data):
        """Update document by ID"""
        update_data['updated_at'] = datetime.now()
        result = self.collection.update_one(
            {"_id": get_object_id(doc_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_by_id(self, doc_id):
        """Delete document by ID"""
        result = self.collection.delete_one({"_id": get_object_id(doc_id)})
        return result.deleted_count > 0

class CategoryManager(BaseMongoModel):
    def __init__(self):
        super().__init__('categories')
    
    def create_category(self, name, description="", parent_id=None):
        """Create a new category"""
        data = {
            'name': name,
            'slug': slugify(name),
            'description': description,
            'parent_id': get_object_id(parent_id) if parent_id else None
        }
        return self.create(data)
    
    def get_by_slug(self, slug):
        return mongo_serializer(
            self.collection.find_one({"slug": slug})
        )
    def find_all(self):
        try:
            # Return all categories, sorted by name
            return self.collection.find({}).sort('name', 1)
        except Exception as e:
            print("Error fetching categories:", str(e))
            return []        
    
class ProductManager(BaseMongoModel):
    def __init__(self):
        super().__init__('products')
    
    def create_product(self, title, category_id, price, description="", variants=None):
        """Create a new product"""
        data = {
            'title': title,
            'slug': self._generate_unique_slug(title),
            'category_id': get_object_id(category_id),
            'price': float(price),
            'description': description,
            'variants': variants or [],
            'images': [],
            'status': 'active',
            'modified_at': datetime.now()
        }
        return self.create(data)
    
    def _generate_unique_slug(self, title):
        """Generate unique slug for product"""
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        
        while self.collection.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def get_by_category(self, category_id, limit=20, skip=0):
        """Get products by category"""
        return self.find_all(
            {"category_id": get_object_id(category_id), "status": "active"},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]
        )
    
    def search_products(self, query, limit=20):
        """Search products by text"""
        cursor = self.collection.find(
            {
                "$text": {"$search": query},
                "status": "active"
            }
        ).limit(limit)
        return mongo_serializer(list(cursor))
    
    def add_variant(self, product_id, variant_data):
        """Add variant to product"""
        return self.collection.update_one(
            {"_id": get_object_id(product_id)},
            {"$push": {"variants": variant_data}}
        ).modified_count > 0

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
        return self.create(data)
    
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
    
    def get_or_create_cart(self, user_id):
        """Get or create cart for user"""
        cart = self.collection.find_one({"user_id": int(user_id)})
        
        if not cart:
            cart_data = {
                'user_id': int(user_id),
                'items': [],
                'total_amount': 0.0
            }
            cart_id = self.create(cart_data)
            cart = self.find_by_id(cart_id)
        else:
            cart = mongo_serializer(cart)
        
        return cart
    
    def add_item(self, user_id, product_id, quantity=1, variant_id=None):
        """Add item to cart"""
        cart = self.get_or_create_cart(user_id)
        
        item_exists = False
        for item in cart['items']:
            if (item['product_id'] == product_id and 
                item.get('variant_id') == variant_id):
                item['quantity'] += quantity
                item_exists = True
                break
        
        if not item_exists:
            new_item = {
                'product_id': product_id,
                'variant_id': variant_id,
                'quantity': quantity,
                'added_at': datetime.now().isoformat()
            }
            cart['items'].append(new_item)
        
        self.collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {"items": cart['items'], "updated_at": datetime.now()}}
        )
        
        return self.get_or_create_cart(user_id)
    
    def remove_item(self, user_id, product_id, variant_id=None):
        """Remove item from cart"""
        return self.collection.update_one(
            {"user_id": int(user_id)},
            {"$pull": {"items": {"product_id": product_id, "variant_id": variant_id}}}
        ).modified_count > 0
    
    def clear_cart(self, user_id):
        """Clear user's cart"""
        return self.collection.update_one(
            {"user_id": int(user_id)},
            {"$set": {"items": [], "updated_at": datetime.now()}}
        ).modified_count > 0

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