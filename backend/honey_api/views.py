from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import Address
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from honey_api.serializer import mongo_serializer, cart_serializer, review_serializer, product_serializer, order_serializer
from mongodb_connector import mongodb
from honey_api.utils import get_object_id, cart_total_amount

from honey_api.mongo_models import CartManager, ReviewManager, OrderManager
from core.serializers import AddressSerializer


@require_http_methods(["GET"])
def index(request):
    try:
        products = mongodb.database['products'].find().limit(3)
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
        reviews = mongodb.database['reviews'].find({"product_slug": slug})
        related_products = mongodb.database['products'].find({
            "category_id": product['category_id'],
            "_id": {"$ne": product['_id']} 
        })

        context = {
            'product': product_serializer(product),
            'reviews': review_serializer(reviews),
            'related_products': mongo_serializer(related_products)
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

        paginator = Paginator(list(mongo_serializer(products)), 4)
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


@require_http_methods(["POST"])
def contact(request):
    try:
        mongodb.database['contacts'].insert_one({
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'message': request.POST.get('message'),
            'date': datetime.now()
        })
        messages.success(request, "Message sent successfully!")
        return redirect('index')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@login_required(login_url='login')
@require_http_methods(["GET"])
def cart_view(request):
    try:
        user_cart = mongodb.database['carts'].find_one({"user_id": request.user.id})

        if not user_cart:
            user_cart = CartManager()
            user_cart.create_cart(request.user.id)        
            user_cart = mongodb.database['carts'].find_one({"user_id": request.user.id})

        context = {
            'cart': cart_serializer(user_cart)
        }

        return render(request, 'cart.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def add_to_cart(request):
    try:
        user_cart = mongodb.database['carts'].find_one({"user_id": request.user.id})

        if not user_cart:
            user_cart = CartManager()
            user_cart.create_cart(request.user.id)        
            user_cart = mongodb.database['carts'].find_one({"user_id": request.user.id})

        data = request.POST
        product_slug = data.get('product_slug')
        quantity = int(data.get('quantity'))

        item_exists = False
        for item in user_cart['items']:
            if item['product_slug'] == product_slug: 
                item['quantity'] += quantity
                item_exists = True
        
        if not item_exists:
            new_item = {
                'product_slug': product_slug,
                'quantity': quantity,
            }
            user_cart['items'].append(new_item)
        
        total_amount = cart_total_amount(user_cart)
        
        mongodb.database['carts'].update_one(
            {"user_id": int(request.user.id)},
            {"$set": {"items": user_cart['items'], "total_amount": total_amount}}
        )

        messages.success(request, "Item successfully added to your cart.")
        return redirect(request.META.get('HTTP_REFERER', '/')) 
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def remove_from_cart(request, slug):
    try:
        user_cart = mongodb.database['carts'].find_one({'user_id': request.user.id})
        items = []

        for item in user_cart['items']:
            if item['product_slug'] != slug:
                items.append(item)

        mongodb.database['carts'].update_one(
            {'user_id': request.user.id},
            {"$set": {"items": items}} 
        )

        messages.success(request, "Item successfully removed from your cart.")
        return redirect(request.META.get('HTTP_REFERER', '/')) 
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def clear_cart(request):
    try:
        user_cart = mongodb.database['carts'].find_one({'user_id': request.user.id})

        if len(user_cart['items']):
            messages.success(request, "Your cart has been successfully cleared.")
        else:
            messages.success(request, "Your cart is already empty.")

        mongodb.database['carts'].update_one(
            {'user_id': request.user.id},
            {"$set": {"items": []}} 
        )

        return redirect(request.META.get('HTTP_REFERER', '/')) 
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@require_http_methods(["POST"])
@login_required(login_url='login')
def add_review(request):
    try:
        data = request.POST
        existing = mongodb.database['reviews'].find_one({
            "user_id": request.user.id,
            "product_slug": data['product_slug']
        }) 

        if existing:
            messages.success(request, "You have already reviewed this product.")
        else:
            review = ReviewManager()
            review.create_review(request.user.id, data['product_slug'], data['rating'], data['comment'])
            messages.success(request, "Your review has been added successfully.")

        return redirect(request.META.get('HTTP_REFERER', '/')) 

    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required(login_url='login')
def checkout(request):
    try:
        user_id = request.user.id
        orders = mongodb.database['orders'].find({'user_id': user_id})
        cart = mongodb.database['carts'].find_one({'user_id': user_id})

        addresses = Address.objects.filter(user=request.user)
        addresses_list = AddressSerializer(addresses, many=True).data
        cart_data = cart_serializer(cart)

        context = {
            'saved_addresses': addresses_list,
            'cart': cart_data,
        }

        return render(request, 'checkout.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)


@require_http_methods(["GET"])
@login_required(login_url='login')
def get_orders(request):
    try:
        user_id = request.user.id
        orders = mongodb.database['orders'].find({'user_id': user_id})
        return order_serializer(orders)
    except Exception as e:
        messages.error(request, str(e))
        return {}


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def create_order(request):
    try:
        data = request.POST
        cart_id = get_object_id(data['cart_id'])

        user_id = request.user.id   
        items = mongodb.database['carts'].find_one({'_id': cart_id})['items']
        total_amount = data['total_amount']
        address_id = data['saved_address']

        order = OrderManager()
        order.create_order(user_id, items, total_amount, address_id)

        mongodb.database['carts'].delete_one({"_id": cart_id}) 

        messages.success(request, "Your order has been placed successfully!")
        return redirect('cart')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)