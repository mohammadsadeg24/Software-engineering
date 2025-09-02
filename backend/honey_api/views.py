from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
import json
from datetime import datetime
from .mongo_models import CartManager, ProductManager, ReviewManager, OrderManager
from django.shortcuts import render, redirect
from django.contrib import messages
from honey_api.serializer import mongo_serializer
from mongodb_connector import mongodb
from honey_api.utils import get_object_id, generate_unique_slug

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
def product_list(request):
    try:
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('q')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        skip = (page - 1) * limit

        if search_query:
            product_list = ProductManager.search_products(search_query, limit)
        elif category_id:
            product_list = ProductManager.get_by_category(category_id, limit, skip)
        else:
            product_list = ProductManager.find_all(
                {"status": "active"},
                limit=limit,
                skip=skip,
                sort=[("created_at", -1)]
            )
        return json_response({"products": product_list, "page": page, "limit": limit})
    except Exception as e:
        return error_response(str(e), 500)

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
@require_http_methods(["GET"])
@login_required
def get_cart(request):
    try:
        user_cart = CartManager.get_or_create_cart(request.user.id)
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
