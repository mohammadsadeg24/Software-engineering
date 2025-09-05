import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'honey_site.settings')
django.setup()

from mongodb_connector import mongodb

def test_mongodb_connection():
    try:
        # Get the MongoDB client
        client = mongodb._client
        
        # Print connection info
        print(f"Connected to MongoDB at: {client.address}")
        
        # Get database
        db = mongodb.database
        print(f"Using database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Try to fetch a document
        category = db.categories.find_one()
        if category:
            print(f"Found category: {category}")
        else:
            print("No categories found")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_mongodb_connection()
