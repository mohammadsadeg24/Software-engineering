# honey_api/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
from .mongo_models import categories, products, reviews, carts, orders
import json
from datetime import datetime

# Helper function
def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False)

def error_response(message, status=400):
    return JsonResponse({"error": message}, status=status)

# Authentication Views
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return json_response({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role
                }
            })
        else:
            return error_response("Invalid credentials", 401)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        data = json.loads(request.body)
        
        # Check if user already exists
        if User.objects.filter(username=data.get('username')).exists():
            return error_response("Username already exists", 400)
        
        if User.objects.filter(email=data.get('email')).exists():
            return error_response("Email already exists", 400)
        
        # Create user
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone_number=data.get('phone_number', ''),
            role=data.get('role', 'member')
        )
        
        return json_response({
            "success": True,
            # "product_id": product_id,
            "message": "Product created successfully"
        })
    except Exception as e:
        return error_response(str(e), 500)

# Review Views
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_review(request):
    try:
        data = json.loads(request.body)
        review_id = reviews.create_review(
            user_id=request.user.id,
            product_id=data.get('product_id'),
            rating=data.get('rating'),
            comment=data.get('comment', '')
        )
        
        return json_response({
            "success": True,
            "review_id": review_id,
            "message": "Review created successfully"
        })
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
def product_reviews(request, product_id):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        skip = (page - 1) * limit
        
        product_reviews = reviews.get_product_reviews(product_id, limit, skip)
        rating_summary = reviews.get_product_rating_summary(product_id)
        
        return json_response({
            "reviews": product_reviews,
            "rating_summary": rating_summary,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return error_response(str(e), 500)

# Cart Views
@require_http_methods(["GET"])
@login_required
def get_cart(request):
    try:
        user_cart = carts.get_or_create_cart(request.user.id)
        
        # Enrich cart items with product details
        enriched_items = []
        total_amount = 0
        
        for item in user_cart.get('items', []):
            product = products.find_by_id(item['product_id'])
            if product:
                enriched_item = {
                    'product': product,
                    'quantity': item['quantity'],
                    'variant_id': item.get('variant_id'),
                    'subtotal': product['price'] * item['quantity']
                }
                enriched_items.append(enriched_item)
                total_amount += enriched_item['subtotal']
        
        user_cart['enriched_items'] = enriched_items
        user_cart['calculated_total'] = total_amount
        
        return json_response(user_cart)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_to_cart(request):
    try:
        data = json.loads(request.body)
        updated_cart = carts.add_item(
            user_id=request.user.id,
            product_id=data.get('product_id'),
            quantity=int(data.get('quantity', 1)),
            variant_id=data.get('variant_id')
        )
        
        return json_response({
            "success": True,
            "message": "Item added to cart",
            "cart": updated_cart
        })
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def remove_from_cart(request, product_id):
    try:
        data = json.loads(request.body) if request.body else {}
        variant_id = data.get('variant_id')
        
        success = carts.remove_item(
            user_id=request.user.id,
            product_id=product_id,
            variant_id=variant_id
        )
        
        if success:
            return json_response({
                "success": True,
                "message": "Item removed from cart"
            })
        else:
            return error_response("Item not found in cart", 404)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clear_cart(request):
    try:
        success = carts.clear_cart(request.user.id)
        if success:
            return json_response({
                "success": True,
                "message": "Cart cleared successfully"
            })
        else:
            return error_response("Failed to clear cart", 500)
    except Exception as e:
        return error_response(str(e), 500)

# Order Views
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_order(request):
    try:
        data = json.loads(request.body)
        
        # Get user's cart
        user_cart = carts.get_or_create_cart(request.user.id)
        if not user_cart.get('items'):
            return error_response("Cart is empty", 400)
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        
        for item in user_cart['items']:
            product = products.find_by_id(item['product_id'])
            if product:
                subtotal = product['price'] * item['quantity']
                order_items.append({
                    'product_id': item['product_id'],
                    'product_title': product['title'],
                    'variant_id': item.get('variant_id'),
                    'quantity': item['quantity'],
                    'unit_price': product['price'],
                    'subtotal': subtotal
                })
                total_amount += subtotal
        
        # Get address data
        address_id = data.get('address_id')
        address_data = None
        if address_id:
            try:
                address = Address.objects.get(id=address_id, user=request.user)
                address_data = {
                    'name': address.name,
                    'address': address.address,
                    'city': address.city,
                    'state': address.state,
                    'country': address.country,
                    'postal_code': address.postal_code
                }
            except Address.DoesNotExist:
                return error_response("Address not found", 404)
        
        # Create order
        order_id = orders.create_order(
            user_id=request.user.id,
            items=order_items,
            total_amount=total_amount,
            address_data=address_data,
            description=data.get('description', '')
        )
        
        # Clear cart after successful order
        carts.clear_cart(request.user.id)
        
        return json_response({
            "success": True,
            "order_id": order_id,
            "message": "Order created successfully"
        })
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
@login_required
def get_orders(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        skip = (page - 1) * limit
        
        user_orders = orders.get_user_orders(request.user.id, limit, skip)
        
        return json_response({
            "orders": user_orders,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
@login_required
def get_order_detail(request, order_id):
    try:
        order = orders.find_by_id(order_id)
        if not order:
            return error_response("Order not found", 404)
        
        # Check if user owns this order or is admin
        if order['user_id'] != request.user.id and request.user.role != 'admin':
            return error_response("Permission denied", 403)
        
        return json_response(order)
    except Exception as e:
        return error_response(str(e), 500)

# Address Views (Django ORM)
@require_http_methods(["GET"])
@login_required
def get_addresses(request):
    try:
        user_addresses = Address.objects.filter(user=request.user).values(
            'id', 'name', 'address', 'city', 'state', 'country', 
            'postal_code', 'is_default', 'created_at'
        )
        return json_response(list(user_addresses))
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_address(request):
    try:
        data = json.loads(request.body)
        
        address = Address.objects.create(
            user=request.user,
            name=data.get('name'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country', 'United States'),
            postal_code=data.get('postal_code'),
            is_default=data.get('is_default', False)
        )
        
        return json_response({
            "success": True,
            "address_id": address.id,
            "message": "Address created successfully"
        })
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_address(request, address_id):
    try:
        data = json.loads(request.body)
        
        address = Address.objects.get(id=address_id, user=request.user)
        
        address.name = data.get('name', address.name)
        address.address = data.get('address', address.address)
        address.city = data.get('city', address.city)
        address.state = data.get('state', address.state)
        address.country = data.get('country', address.country)
        address.postal_code = data.get('postal_code', address.postal_code)
        address.is_default = data.get('is_default', address.is_default)
        
        address.save()
        
        return json_response({
            "success": True,
            "message": "Address updated successfully"
        })
    except Address.DoesNotExist:
        return error_response("Address not found", 404)
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["DELETE"])
@login_required
def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.delete()
        
        return json_response({
            "success": True,
            "message": "Address deleted successfully"
        })
    except Address.DoesNotExist:
        return error_response("Address not found", 404)
    except Exception as e:
        return error_response(str(e), 500)

# User Profile Views
@require_http_methods(["GET"])
@login_required
def get_profile(request):
    try:
        user_data = {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone_number": request.user.phone_number,
            "role": request.user.role,
            "created_at": request.user.created_at.isoformat(),
            "updated_at": request.user.updated_at.isoformat()
        }
        return json_response(user_data)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_profile(request):
    try:
        data = json.loads(request.body)
        
        request.user.first_name = data.get('first_name', request.user.first_name)
        request.user.last_name = data.get('last_name', request.user.last_name)
        request.user.phone_number = data.get('phone_number', request.user.phone_number)
        request.user.email = data.get('email', request.user.email)
        
        request.user.save()
        
        return json_response({
            "success": True,
            "message": "Profile updated successfully"
        })
    except Exception as e:
        return error_response(str(e), 500),
        #     "message": "User created successfully",
        #     "user": {
        #         "id": user.id,
        #         "username": user.username,
        #         "email": user.email
        #     }
        # })
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return json_response({"success": True, "message": "Logged out successfully"})

# Category Views
@require_http_methods(["GET"])
def category_list(request):
    try:
        parent_id = request.GET.get('parent_id')
        if parent_id == 'null' or parent_id == '':
            parent_id = None
            
        if parent_id:
            category_list = categories.get_children(parent_id)
        else:
            category_list = categories.get_root_categories()
            
        return json_response(category_list)
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
def category_detail(request, slug):
    try:
        category = categories.get_by_slug(slug)
        if not category:
            return error_response("Category not found", 404)
        return json_response(category)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_category(request):
    try:
        if request.user.role != 'admin':
            return error_response("Permission denied", 403)
            
        data = json.loads(request.body)
        category_id = categories.create_category(
            name=data.get('name'),
            description=data.get('description', ''),
            parent_id=data.get('parent_id')
        )
        
        return json_response({
            "success": True,
            "category_id": category_id,
            "message": "Category created successfully"
        })
    except Exception as e:
        return error_response(str(e), 500)

# Product Views
@require_http_methods(["GET"])
def product_list(request):
    try:
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('q')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        skip = (page - 1) * limit
        
        if search_query:
            product_list = products.search_products(search_query, limit)
        elif category_id:
            product_list = products.get_by_category(category_id, limit, skip)
        else:
            product_list = products.find_all(
                {"status": "active"},
                limit=limit,
                skip=skip,
                sort=[("created_at", -1)]
            )
        
        return json_response({
            "products": product_list,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        return error_response(str(e), 500)

@require_http_methods(["GET"])
def product_detail(request, slug):
    try:
        product = products.get_by_slug(slug)
        if not product:
            return error_response("Product not found", 404)
        
        # Get product reviews and rating summary
        product_reviews = reviews.get_product_reviews(product['id'])
        rating_summary = reviews.get_product_rating_summary(product['id'])
        
        product['reviews'] = product_reviews
        product['rating_summary'] = rating_summary
        
        return json_response(product)
    except Exception as e:
        return error_response(str(e), 500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_product(request):
    try:
        if request.user.role != 'admin':
            return error_response("Permission denied", 403)
            
        data = json.loads(request.body)
        product_id = products.create_product(
            title=data.get('title'),
            category_id=data.get('category_id'),
            price=data.get('price'),
            description=data.get('description', ''),
            variants=data.get('variants', [])
        )
        
        return json_response({
            "success": True,
            "product_id": product_id,
            "message": "Product created successfully"
        })
    except Exception as e:
        return error_response(str(e), 500)