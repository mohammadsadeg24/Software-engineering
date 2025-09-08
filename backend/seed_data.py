import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "honey_site.settings")  
django.setup()

from honey_api.mongo_models import CategoryManager, ProductManager, ReviewManager, CartManager, OrderManager
from datetime import datetime

# Constants
USER_ID = 1
ADDRESS_ID = 14

# Initialize managers
categories = CategoryManager()
products = ProductManager()
reviews = ReviewManager()
carts = CartManager()
orders = OrderManager()

# Clear collections
categories.collection.delete_many({})
products.collection.delete_many({})
reviews.collection.delete_many({})
carts.collection.delete_many({})
orders.collection.delete_many({})

now = datetime.now()

# --- Categories ---
categories_list = [
    {"name": "Raw Honey"},
    {"name": "Flavored Honey"},
    {"name": "Organic Honey"},
    {"name": "Honey Comb"},
]

category_ids = {}
for cat in categories_list:
    categories.create_category(cat["name"])  # create category
    # fetch the category from DB by name to get its ID
    cat_doc = categories.collection.find_one({"name": cat["name"]})
    category_ids[cat["name"]] = str(cat_doc["_id"])


# --- Products ---
product_list = [
    {"title": "Wildflower Raw Honey", "category": "Raw Honey", "price": 12.99, "description": "Pure wildflower honey harvested from local farms"},
    {"title": "Clover Raw Honey", "category": "Raw Honey", "price": 10.99, "description": "Smooth and mild clover honey"},
    {"title": "Manuka Honey", "category": "Raw Honey", "price": 29.99, "description": "Premium Manuka honey from New Zealand"},
    {"title": "Cinnamon Infused Honey", "category": "Flavored Honey", "price": 15.99, "description": "Raw honey infused with Ceylon cinnamon"},
    {"title": "Lavender Honey", "category": "Flavored Honey", "price": 16.99, "description": "Delicate honey with natural lavender essence"},
    {"title": "Ginger Infused Honey", "category": "Flavored Honey", "price": 14.99, "description": "Honey with natural ginger flavor"},
    {"title": "Organic Forest Honey", "category": "Organic Honey", "price": 18.99, "description": "100% certified organic forest honey"},
    {"title": "Acacia Honey", "category": "Organic Honey", "price": 19.99, "description": "Light and sweet organic acacia honey"},
    {"title": "Honey Comb Piece", "category": "Honey Comb", "price": 25.99, "description": "Natural honey comb, fresh and unprocessed"},
    {"title": "Mini Honey Comb", "category": "Honey Comb", "price": 9.99, "description": "Small portion of honey comb for tasting"},
]

for p in product_list:
    cat_id = category_ids[p["category"]]
    products.create_product(p["title"], cat_id, p["price"], p["description"])

# --- Reviews ---
reviews_data = [
    {"slug": "wildflower-raw-honey", "rating": 5, "comment": "Absolutely delicious! Best honey I've ever tasted."},
    {"slug": "wildflower-raw-honey", "rating": 4, "comment": "Great quality honey, fast delivery."},
    {"slug": "manuka-honey", "rating": 5, "comment": "Premium taste, worth the price."},
    {"slug": "cinnamon-infused-honey", "rating": 5, "comment": "The cinnamon flavor is perfect, not too strong."},
    {"slug": "lavender-honey", "rating": 4, "comment": "Nice lavender aroma, very smooth."},
    {"slug": "organic-forest-honey", "rating": 5, "comment": "Organic taste is amazing!"},
    {"slug": "acacia-honey", "rating": 5, "comment": "Light and sweet, perfect for tea."},
    {"slug": "honey-comb-piece", "rating": 5, "comment": "Fresh and natural, loved it!"},
]

for r in reviews_data:
    reviews.create_review(USER_ID, r["slug"], r["rating"], r["comment"])

# --- Cart ---
carts.create_cart(USER_ID)

# --- Orders ---
order_list = [
    {
        "items": [
            {"product_slug": "clover-raw-honey", "quantity": 2, "price": 10.99},
            {"product_slug": "cinnamon-infused-honey", "quantity": 1, "price": 15.99},
        ],
        "total_amount": 37.97
    },
    {
        "items": [
            {"product_slug": "organic-forest-honey", "quantity": 1, "price": 18.99},
            {"product_slug": "acacia-honey", "quantity": 1, "price": 19.99},
        ],
        "total_amount": 38.98
    },
    {
        "items": [
            {"product_slug": "honey-comb-piece", "quantity": 1, "price": 25.99},
            {"product_slug": "mini-honey-comb", "quantity": 3, "price": 9.99},
        ],
        "total_amount": 55.96
    }
]

for o in order_list:
    orders.create_order(USER_ID, o["items"], o["total_amount"], ADDRESS_ID)

print("Seed data inserted successfully!")
