from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
import json
from datetime import datetime
from django.shortcuts import render, redirect
from honey_api.serializer import mongo_serializer
from mongodb_connector import mongodb
from django.shortcuts import render, redirect
from django.contrib import messages
from honey_api.utils import get_object_id, generate_unique_slug

@require_http_methods(["GET"])
def home(request):
    try:
        category = request.GET.get('category_id', None)

        if category is None:
            product_list = mongo_serializer(mongodb.database['products'].find())
        else:
            product_list = mongo_serializer(mongodb.database['products'].find({"category_id": get_object_id(category)}))
        
        return render(request, 'home.html', {'product_list': product_list})

    except Exception as e:
        message = {'detail': str(e)}
        return render(request, '404.html', message, status=404)

@require_http_methods(["GET"])
def category_list(request):
    try:
        category_list = mongo_serializer(mongodb.database['categories'].find())

        print(category_list)        

        return render(request, 'home.html', {'category_list': category_list})

    except Exception as e:
        message = {'detail': str(e)}
        return render(request, '404.html', message, status=404)

@csrf_exempt
@require_http_methods(["POST"])
# @login_required
def create_category(request):
    try:
        # if request.user.role != 'admin':
        # return render(request, '404.html', message, status=403)
            
        data = json.loads(request.body)
        record = {
            'name': data.get('name'),
            'slug': generate_unique_slug(collection='categories', title=data.get('name')),
            'description': data.get('description', ''),
            'parent_id': get_object_id(data.get('parent_id')) if data.get('parent_id') else None
        }
        category_id = mongodb.database['categories'].insert_one(record)
        
        return render(request, 'home.html', {})

    except Exception as e:
        message = {'detail': str(e)}
        return render(request, '404.html', message, status=505)

@require_http_methods(["GET"])
def category_detail(request, slug):
    try:
        category = mongo_serializer(mongodb.database['categories'].find_one({'slug': slug}))

        if category is None:
            raise ValueError(f"Category with slug '{slug}' not found.")

        return render(request, 'home.html', {'category': category})

    except Exception as e:
        message = {'detail': str(e)}
        return render(request, '404.html', message, status=404)
@login_required
def profile_view(request):
    try:
        # Assuming User model has profile data; adjust if using MongoDB
        user_data = {
            'user': request.user,
        }
        return render(request, 'profile.html', user_data)
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=404)

@require_http_methods(["POST"])
def contact_view(request):
    try:
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        # Save to MongoDB or send email (implement as needed)
        mongodb.database['contacts'].insert_one({
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
            'date': datetime.now()
        })
        messages.success(request, "Message sent successfully!")
        return redirect('home')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)

@login_required
def edit_profile_view(request):
    if request.method == "POST":
        # Handle form submission to update user data
        try:
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            # Update phone_number in profile or MongoDB
            # Example: user.profile.phone_number = request.POST.get('phone_number')
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'profile.html', {'error': str(e)})
    return render(request, 'edit_profile.html', {'user': request.user})

# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def create_review(request):
#     try:
#         data = json.loads(request.body)

#         record = {
#             'user_id': int(request.user.id) or 12,
#             'product_id': get_object_id(data.get('product_id')) or 12,
#             'rating': int(data.get('rating')) or 12,
#             'comment': data.get('comment', '') or "text",
#             'date': datetime.now()
#         }

#         inserted_id = reviews.collection.insert_one(record)
        
#         return json_response({
#             "success": True,
#             "review_id": inserted_id,
#             "message": "Review created successfully"
#         })
#     except ValueError as e:
#         return error_response(str(e), 400)
#     except Exception as e:
#         return error_response(str(e), 500)

# @require_http_methods(["GET"])
# def product_reviews(request, product_id):
#     try:
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 10))
#         skip = (page - 1) * limit
        
#         product_reviews = reviews.get_product_reviews(product_id, limit, skip)
#         rating_summary = reviews.get_product_rating_summary(product_id)
        
#         return json_response({
#             "reviews": product_reviews,
#             "rating_summary": rating_summary,
#             "page": page,
#             "limit": limit
#         })
#     except Exception as e:
#         return error_response(str(e), 500)

# # Cart Views
# @require_http_methods(["GET"])
# @login_required
# def get_cart(request):
#     try:
#         user_cart = carts.get_or_create_cart(request.user.id)
        
#         # Enrich cart items with product details
#         enriched_items = []
#         total_amount = 0
        
#         for item in user_cart.get('items', []):
#             product = products.find_by_id(item['product_id'])
#             if product:
#                 enriched_item = {
#                     'product': product,
#                     'quantity': item['quantity'],
#                     'variant_id': item.get('variant_id'),
#                     'subtotal': product['price'] * item['quantity']
#                 }
#                 enriched_items.append(enriched_item)
#                 total_amount += enriched_item['subtotal']
        
#         user_cart['enriched_items'] = enriched_items
#         user_cart['calculated_total'] = total_amount
        
#         return json_response(user_cart)
#     except Exception as e:
#         return error_response(str(e), 500)

# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def add_to_cart(request):
#     try:
#         data = json.loads(request.body)
#         updated_cart = carts.add_item(
#             user_id=request.user.id,
#             product_id=data.get('product_id'),
#             quantity=int(data.get('quantity', 1)),
#             variant_id=data.get('variant_id')
#         )
        
#         return json_response({
#             "success": True,
#             "message": "Item added to cart",
#             "cart": updated_cart
#         })
#     except Exception as e:
#         return error_response(str(e), 500)

# @csrf_exempt
# @require_http_methods(["DELETE"])
# @login_required
# def remove_from_cart(request, product_id):
#     try:
#         data = json.loads(request.body) if request.body else {}
#         variant_id = data.get('variant_id')
        
#         success = carts.remove_item(
#             user_id=request.user.id,
#             product_id=product_id,
#             variant_id=variant_id
#         )
        
#         if success:
#             return json_response({
#                 "success": True,
#                 "message": "Item removed from cart"
#             })
#         else:
#             return error_response("Item not found in cart", 404)
#     except Exception as e:
#         return error_response(str(e), 500)

# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def clear_cart(request):
#     try:
#         success = carts.clear_cart(request.user.id)
#         if success:
#             return json_response({
#                 "success": True,
#                 "message": "Cart cleared successfully"
#             })
#         else:
#             return error_response("Failed to clear cart", 500)
#     except Exception as e:
#         return error_response(str(e), 500)

# # Order Views
# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def create_order(request):
#     try:
#         data = json.loads(request.body)
        
#         # Get user's cart
#         user_cart = carts.get_or_create_cart(request.user.id)
#         if not user_cart.get('items'):
#             return error_response("Cart is empty", 400)
        
#         # Calculate total amount
#         total_amount = 0
#         order_items = []
        
#         for item in user_cart['items']:
#             product = products.find_by_id(item['product_id'])
#             if product:
#                 subtotal = product['price'] * item['quantity']
#                 order_items.append({
#                     'product_id': item['product_id'],
#                     'product_title': product['title'],
#                     'variant_id': item.get('variant_id'),
#                     'quantity': item['quantity'],
#                     'unit_price': product['price'],
#                     'subtotal': subtotal
#                 })
#                 total_amount += subtotal
        
#         # Get address data
#         address_id = data.get('address_id')
#         address_data = None
#         if address_id:
#             try:
#                 address = Address.objects.get(id=address_id, user=request.user)
#                 address_data = {
#                     'name': address.name,
#                     'address': address.address,
#                     'city': address.city,
#                     'state': address.state,
#                     'country': address.country,
#                     'postal_code': address.postal_code
#                 }
#             except Address.DoesNotExist:
#                 return error_response("Address not found", 404)
        
#         # Create order
#         order_id = orders.create_order(
#             user_id=request.user.id,
#             items=order_items,
#             total_amount=total_amount,
#             address_data=address_data,
#             description=data.get('description', '')
#         )
        
#         # Clear cart after successful order
#         carts.clear_cart(request.user.id)
        
#         return json_response({
#             "success": True,
#             "order_id": order_id,
#             "message": "Order created successfully"
#         })
#     except Exception as e:
#         return error_response(str(e), 500)

# @require_http_methods(["GET"])
# @login_required
# def get_orders(request):
#     try:
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 10))
#         skip = (page - 1) * limit
        
#         user_orders = orders.get_user_orders(request.user.id, limit, skip)
        
#         return json_response({
#             "orders": user_orders,
#             "page": page,
#             "limit": limit
#         })
#     except Exception as e:
#         return error_response(str(e), 500)

# @require_http_methods(["GET"])
# @login_required
# def get_order_detail(request, order_id):
#     try:
#         order = orders.find_by_id(order_id)
#         if not order:
#             return error_response("Order not found", 404)
        
#         # Check if user owns this order or is admin
#         if order['user_id'] != request.user.id and request.user.role != 'admin':
#             return error_response("Permission denied", 403)
        
#         return json_response(order)
#     except Exception as e:
#         return error_response(str(e), 500)




# # Product Views
# @require_http_methods(["GET"])
# def product_list(request):
#     try:
#         category_id = request.GET.get('category_id')
#         search_query = request.GET.get('q')
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 20))
#         skip = (page - 1) * limit
        
#         if search_query:
#             product_list = products.search_products(search_query, limit)
#         elif category_id:
#             product_list = products.get_by_category(category_id, limit, skip)
#         else:
#             product_list = products.find_all(
#                 {"status": "active"},
#                 limit=limit,
#                 skip=skip,
#                 sort=[("created_at", -1)]
#             )
        
#         return json_response({
#             "products": product_list,
#             "page": page,
#             "limit": limit
#         })
#     except Exception as e:
#         return error_response(str(e), 500)

# @require_http_methods(["GET"])
# def product_detail(request, slug):
#     try:
#         product = products.get_by_slug(slug)
#         if not product:
#             return error_response("Product not found", 404)
        
#         # Get product reviews and rating summary
#         product_reviews = reviews.get_product_reviews(product['id'])
#         rating_summary = reviews.get_product_rating_summary(product['id'])
        
#         product['reviews'] = product_reviews
#         product['rating_summary'] = rating_summary
        
#         return json_response(product)
#     except Exception as e:
#         return error_response(str(e), 500)

# @csrf_exempt
# @require_http_methods(["POST"])
# @login_required
# def create_product(request):
#     try:
#         if request.user.role != 'admin':
#             return error_response("Permission denied", 403)
            
#         data = json.loads(request.body)
#         product_id = products.create_product(
#             title=data.get('title'),
#             category_id=data.get('category_id'),
#             price=data.get('price'),
#             description=data.get('description', ''),
#             variants=data.get('variants', [])
#         )
        
#         return json_response({
#             "success": True,
#             "product_id": product_id,
#             "message": "Product created successfully"
#         })
#     except Exception as e:
#         return error_response(str(e), 500)