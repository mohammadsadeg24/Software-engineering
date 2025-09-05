from itertools import product
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
import json
from datetime import datetime
from .mongo_models import CartManager, ProductManager, ReviewManager, OrderManager, CategoryManager
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from honey_api.serializer import mongo_serializer
from mongodb_connector import mongodb
from honey_api.utils import get_object_id, generate_unique_slug
from django.shortcuts import render
from .mongo_models import ProductManager

# -------------------------
# Index View (for enhanced template)
# -------------------------
@require_http_methods(["GET"])
def index(request):
    try:
        pm = ProductManager()
        # Get featured products (limit to 3)
        # featured_products = pm.get_featured_products()[:3]
        featured_products = pm.find_all()[:3]
        context = {
            'featured_products': featured_products,
        }
        return render(request, 'index.html', context)
    except Exception as e:
        print("Error in index view:", str(e))
        context = {
            'featured_products': [],
        }
        return render(request, 'index.html', context)

@require_http_methods(["GET"])
def debug_categories(request):
    try:
        cm = CategoryManager()
        categories = list(cm.find_all())
        return JsonResponse({
            'count': len(categories),
            'categories': mongo_serializer(categories)
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
# -------------------------
# Product Views
# -------------------------
# Renamed and updated the function to implement search, category filtering, and sorting
@require_http_methods(["GET"])
def honey_shop_view(request):
    
    try:
        print("Starting honey_shop_view...")

        # Get query parameters
        search_query = request.GET.get('q', '').strip()
        category_slug = request.GET.get('category', '').strip()
        sort_by = request.GET.get('sort', 'title').strip()  # Changed default sort to 'title'
        page_number = request.GET.get('page', 1)
        
        print(f"Query parameters: search={search_query}, category={category_slug}, sort={sort_by}, page={page_number}")
        
        
        # Initialize managers
        pm = ProductManager()
        cm = CategoryManager()
        
        # Base query for active products (temporarily remove status filter for testing)
        query = {}  # Removed status filter temporarily to see all products
        
        # Apply search filter
        if search_query:
            query['title'] = {'$regex': search_query, '$options': 'i'}  # Changed 'name' to 'title'
        
        print(f"Initial query: {query}")
        
        # Apply category filter
        if category_slug:
            category_obj = cm.collection.find_one({'slug': category_slug})
            print(f"Found category: {category_obj}")
            if category_obj:
                query['category_id'] = category_obj['_id']
        
        # Determine sorting order
        sort_field = 'title'  # Changed default sort field to 'title'
        sort_direction = 1
        if sort_by:
            if sort_by.startswith('-'):
                sort_field = sort_by[1:]
                sort_direction = -1
            else:
                sort_field = sort_by
        
        # Get all products matching the criteria
        all_products = pm.find_all(query, sort=[(sort_field, sort_direction)])
        
        # Convert MongoDB documents to make them template-friendly
        processed_products = []
        for product in all_products:
            # Convert _id to id for template access
            product['id'] = str(product.get('_id'))
            if 'variants' in product and product['variants']:
                for variant in product['variants']:
                    if '_id' in variant:
                        variant['id'] = str(variant['_id'])
            processed_products.append(product)
        
        # Pagination
        paginator = Paginator(processed_products, 12) # Show 12 products per page
        products_page = paginator.get_page(page_number)
        
        # Fetch all categories for the filter links
        all_categories_cursor = cm.find_all()
        # print("Categories found:", list(all_categories))

        # Convert products to list for debugging
        products_list = list(products_page)
        all_categories_list = list(all_categories_cursor)
        print("Categories found:", all_categories_list)

        context = {
            'products': products_page,
            'categories': all_categories_list,
            'search_query': search_query,
            'selected_category_slug': category_slug,
            'sort_by': sort_by,
            'debug': True,  # Enable debug output
            'products_debug': products_list[:2] if products_list else []  # Show first 2 products for debugging
        }
        
        # Debug print
        print(f"Number of products: {len(products_list)}")
        if products_list:
            print(f"Sample product: {products_list[0]}")
            
        return render(request, 'shop.html', context)
        
    except Exception as e:
        print("Error in honey_shop_view:", str(e))
        messages.error(request, "An error occurred while loading the shop page.")
        return render(request, 'shop.html', {'products': [], 'categories': []})



@require_http_methods(["GET"])
def product_detail(request, product_id):
    try:
        pm = ProductManager()
        product = pm.find_by_id(product_id)
        
        if not product:
            messages.error(request, "Product not found.")
            return redirect('shop')
            
        # Convert MongoDB _id to string id for template
        product['id'] = str(product.get('_id'))
        if 'variants' in product and product['variants']:
            for variant in product['variants']:
                if '_id' in variant:
                    variant['id'] = str(variant['_id'])
                    
        context = {
            'product': product,
        }
        return render(request, 'product_detail.html', context)
        
    except Exception as e:
        print("Error in product_detail:", str(e))
        messages.error(request, "An error occurred while loading the product.")
        return redirect('shop')

def product_list(request):
    pm = ProductManager()
    print("DEBUG pm.collection:", type(pm.collection))  # should be Collection
    products = pm.find_all()  # or find_all
    print("DEBUG products:", type(products))            # should be list, not dict
    return render(request, "products.html", {"products":      products})

# -------------------------
# Helpers
# -------------------------
def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False)

def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status)

# -------------------------
# Home / Categories
# -------------------------
@require_http_methods(["GET"])
def home(request):
    try:
        category = request.GET.get('category_id')
        if category:
            product_list = mongo_serializer(
                mongodb.database['products'].find({"category_id": get_object_id(category)})
            )
        else:
            product_list = mongo_serializer(mongodb.database['products'].find())
        
        # Add print statement for debugging
        print("Products found:", product_list)
        
        context = {
            'product_list': product_list,
            'page_title': 'Home'
        }
        return render(request, 'home.html', context)
    except Exception as e:
        print("Error in home view:", str(e))  # Debug print
        return render(request, '404.html', {'detail': str(e)}, status=404)

@require_http_methods(["GET"])
def category_list(request):
    try:
        category_list = mongo_serializer(mongodb.database['categories'].find())
        return render(request, 'home.html', {'category_list': category_list})
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def create_category(request):
    try:
        data = json.loads(request.body)
        record = {
            'name': data.get('name'),
            'slug': generate_unique_slug(collection='categories', title=data.get('name')),
            'description': data.get('description', ''),
            'parent_id': get_object_id(data.get('parent_id')) if data.get('parent_id') else None
        }
        mongodb.database['categories'].insert_one(record)
        return redirect('category_list')
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=500)

@require_http_methods(["GET"])
def category_detail(request, slug):
    try:
        category = mongo_serializer(mongodb.database['categories'].find_one({'slug': slug}))
        if not category:
            raise ValueError(f"Category with slug '{slug}' not found.")
        return render(request, 'home.html', {'category': category})
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)

# -------------------------
# Profile
# -------------------------
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user, 'page_title': 'Profile'})

@login_required
def edit_profile_view(request):
    if request.method == "POST":
        try:
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'profile.html', {'error': str(e)})
    return render(request, 'edit_profile.html', {'user': request.user})

# -------------------------
# Test MongoDB Connection
# -------------------------
def test_mongodb(request):
    try:
        # Test the connection
        result = mongodb.database.list_collection_names()
        collections = list(result)
        return JsonResponse({
            'status': 'success',
            'message': 'MongoDB connection successful',
            'collections': collections
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'MongoDB connection failed: {str(e)}'
        }, status=500)

# -------------------------
# Contact
# -------------------------
@require_http_methods(["POST"])
def contact_view(request):
    try:
        mongodb.database['contacts'].insert_one({
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'message': request.POST.get('message'),
            'date': datetime.now()
        })
        messages.success(request, "Message sent successfully!")
        return redirect('home')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)

# -------------------------
# Product & Reviews
# -------------------------
@require_http_methods(["GET"])
def product_reviews(request, product_id):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        skip = (page - 1) * limit
        product_reviews = ReviewManager.get_product_reviews(product_id, limit, skip)
        rating_summary = ReviewManager.get_product_rating_summary(product_id)
        return json_response({
            "reviews": product_reviews,
            "rating_summary": rating_summary,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------
# Cart
# -------------------------
@login_required
def cart_view(request):
    try:
        cart_manager = CartManager()
        user_cart = cart_manager.get_or_create_cart(request.user.id)
        return render(request, 'cart.html', {'cart': user_cart})
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'cart.html', {'cart': None})

@require_http_methods(["GET"])
@login_required
def get_cart(request):
    try:
        cart_manager = CartManager()
        user_cart = cart_manager.get_or_create_cart(request.user.id)
        return json_response(user_cart)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        updated_cart = CartManager.add_item(
            user_id=request.user.id,
            product_id=data.get('product_id'),
            quantity=int(data.get('quantity', 1))
        )
        return json_response({"success": True, "cart": updated_cart})
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def remove_from_cart(request, product_id):
    try:
        success = CartManager.remove_item(request.user.id, product_id)
        if success:
            return json_response({"success": True, "message": "Item removed"})
        return error_response("Item not found", 404)
    except Exception as e:
        return error_response(str(e), 500)

# -------------------------
# Orders
# -------------------------
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_order(request):
    try:
        data = json.loads(request.body)
        order_id = OrderManager.create_order(
            user_id=request.user.id,
            address_id=data.get('address_id'),
            description=data.get('description', '')
        )
        CartManager.clear_cart(request.user.id)
        return json_response({"success": True, "order_id": order_id})
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
@login_required
def get_orders(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        skip = (page - 1) * limit
        user_orders = OrderManager.get_user_orders(request.user.id, limit, skip)
        return json_response({"orders": user_orders, "page": page, "limit": limit})
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
@login_required
def get_order_detail(request, order_id):
    try:
        order = OrderManager.find_by_id(order_id)
        if not order:
            return error_response("Order not found", 404)
        if order['user_id'] != request.user.id and request.user.role != 'admin':
            return error_response("Permission denied", 403)
        return json_response(order)
    except Exception as e:
        return error_response(str(e), 500)