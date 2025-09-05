#!/usr/bin/env python3
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['honey_site']

# Clear existing data to avoid duplicates
db.categories.delete_many({})
db.products.delete_many({})
db.reviews.delete_many({})
db.carts.delete_many({})
db.orders.delete_many({})
print("Cleared existing data")

# Insert categories
categories = [
    {"name": "Raw Honey", "slug": "raw-honey"},
    {"name": "Flavored Honey", "slug": "flavored-honey"},
]

category_result = db.categories.insert_many(categories)
print(f"Inserted categories: {category_result.inserted_ids}")

# Get category IDs
raw_honey_id = category_result.inserted_ids[0]
flavored_honey_id = category_result.inserted_ids[1]

# Insert products
now = datetime.utcnow()
products = [
    {
        "title": "Wildflower Raw Honey",
        "slug": "wildflower-raw-honey",
        "category_id": raw_honey_id,
        "price": 12.99,
        "description": "Pure wildflower honey harvested from local farms",
        "status": "active",
        "created_at": now,
        "updated_at": now
    },
    {
        "title": "Clover Raw Honey",
        "slug": "clover-raw-honey",
        "category_id": raw_honey_id,
        "price": 10.99,
        "description": "Smooth and mild clover honey",
        "status": "active",
        "created_at": now,
        "updated_at": now
    },
    {
        "title": "Cinnamon Infused Honey",
        "slug": "cinnamon-infused-honey",
        "category_id": flavored_honey_id,
        "price": 15.99,
        "description": "Raw honey infused with Ceylon cinnamon",
        "status": "active",
        "created_at": now,
        "updated_at": now
    },
    {
        "title": "Lavender Honey",
        "slug": "lavender-honey",
        "category_id": flavored_honey_id,
        "price": 16.99,
        "description": "Delicate honey with natural lavender essence",
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
]

product_result = db.products.insert_many(products)
print(f"Inserted products: {product_result.inserted_ids}")

# Insert reviews
reviews = [
    {
        "user_id": ObjectId(),
        "product_id": product_result.inserted_ids[0],  # Wildflower Raw Honey
        "rating": 5,
        "comment": "Absolutely delicious! Best honey I've ever tasted.",
        "date": now,
        "created_at": now,
        "updated_at": now
    },
    {
        "user_id": ObjectId(),
        "product_id": product_result.inserted_ids[0],  # Wildflower Raw Honey
        "rating": 4,
        "comment": "Great quality honey, fast delivery.",
        "date": now,
        "created_at": now,
        "updated_at": now
    },
    {
        "user_id": ObjectId(),
        "product_id": product_result.inserted_ids[2],  # Cinnamon Infused Honey
        "rating": 5,
        "comment": "The cinnamon flavor is perfect, not too strong.",
        "date": now,
        "created_at": now,
        "updated_at": now
    }
]

review_result = db.reviews.insert_many(reviews)
print(f"Inserted reviews: {review_result.inserted_ids}")

# Insert cart
user_id_1 = ObjectId()

cart_items = [
    {
        "product_id": product_result.inserted_ids[0],  # Wildflower Raw Honey
        "variant_id": None,
        "quantity": 2,
        "added_at": now
    },
    {
        "product_id": product_result.inserted_ids[3],  # Lavender Honey
        "variant_id": None,
        "quantity": 1,
        "added_at": now
    }
]

cart = {
    "user_id": user_id_1,
    "items": cart_items,
    "total_amount": 42.97,  # (12.99 * 2) + 16.99
    "created_at": now,
    "updated_at": now
}

cart_result = db.carts.insert_one(cart)
print(f"Inserted cart: {cart_result.inserted_id}")

# Insert order
order_items = [
    {
        "product_id": product_result.inserted_ids[1],  # Clover Raw Honey
        "quantity": 3,
        "price": 10.99
    },
    {
        "product_id": product_result.inserted_ids[2],  # Cinnamon Infused Honey
        "quantity": 1,
        "price": 15.99
    }
]

order = {
    "user_id": user_id_1,
    "items": order_items,
    "total_amount": 48.96,  # (10.99 * 3) + 15.99
    "payment_status": "paid",
    "order_status": "shipped",
    "description": "Honey variety pack order",
    "address": {
        "street": "123 Main Street",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62701"
    },
    "order_number": "ORD-2024-001",
    "transaction_ref": "TXN-ABC123456",
    "created_at": now,
    "updated_at": now
}

order_result = db.orders.insert_one(order)
print(f"Inserted order: {order_result.inserted_id}")

client.close()
print("Seed data inserted successfully!")