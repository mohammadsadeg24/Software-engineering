from itertools import product
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from honey_api.serializer import mongo_serializer
from mongodb_connector import mongodb
from honey_api.utils import get_object_id, generate_unique_slug
from django.shortcuts import render

from .mongo_models import CartManager, ProductManager, ReviewManager, OrderManager, CategoryManager

@require_http_methods(["GET"])
def index(request):
    try:
        products = mongodb.database['products'].find().limit(4)
        categories = mongodb.database['categories'].find()

        context = {
            'featured_products': mongo_serializer(products),
            'categories': mongo_serializer(categories)
        }

        return render(request, 'index.html', context)

    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)


@require_http_methods(["GET"])
def category_list(request):
    try:
        categories = mongodb.database['categories'].find()

        context = {
            'categories': mongo_serializer(categories)
        }

        return render(request, 'index.html', context)
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)


@require_http_methods(["GET"])
def product_list(request):
    try:
        products = mongodb.database['products'].find()

        context = {
            'products': mongo_serializer(products),
        }

        return render(request, 'products.html', context)

    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)


@require_http_methods(["GET"])
def product_detail(request, slug):
    try:
        product = mongodb.database['products'].find_one({"slug": slug})

        
        context = {
            'product': product,
        }

        return render(request, 'product_detail.html', context)
        
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)


@require_http_methods(["GET"])
def shop(request):
    try:
        search_query = request.GET.get('q')
        category_slug = request.GET.get('category')
        sort_by = request.GET.get('sort', 'title')
        page_number = request.GET.get('page', 1)
        
        filters = {}
        
        if search_query:
            filters['title'] = {'$regex': search_query, '$options': 'i'} 
        
        if category_slug:
            category_obj = mongodb.database['categories'].find_one({'slug': category_slug})
            if category_obj:
                filters['category_id'] = category_obj['_id']
        
        sort_field = 'title' 
        sort_direction = 1
        if sort_by:
            if sort_by.startswith('-'):
                sort_field = sort_by[1:]
                sort_direction = -1
            else:
                sort_field = sort_by

        products = mongodb.database['products'].find(filters, sort=[(sort_field, sort_direction)])
        categories = mongodb.database['categories'].find()

        paginator = Paginator(list(mongo_serializer(products)), 2)
        products_page = paginator.get_page(page_number)
        
        context = {
            'products': products_page,
            'categories': mongo_serializer(categories),
            'search_query': search_query,
            'selected_category_slug': category_slug,
            'sort_by': sort_by,
        }
        
        return render(request, 'shop.html', context)
        
    except Exception as e:
        return render(request, '404.html', {'detail': str(e)}, status=404)


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