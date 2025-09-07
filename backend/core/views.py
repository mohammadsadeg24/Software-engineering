from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from core.models import User, Address
import json
from django.contrib import messages
from django.shortcuts import render, redirect

from core.serializers import AddressSerializer
from django.views.decorators.http import require_POST

from honey_api.views import get_orders
from mongodb_connector import mongodb

@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_user(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {username}")
                return redirect('index')
                
            else:
                messages.success(request, "Invalid username or password. Please try again.")
                return redirect('index')
        else:
            # login page
            return render(request, '404.html', {'detail': str(e)}, status=500)            
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@csrf_exempt
@require_http_methods(["GET", "POST"])
def register_user(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            
            if User.objects.filter(username=data.get('username')).exists() or \
            User.objects.filter(email=data.get('email')).exists():
                messages.error("Username or email already exists.")
                # register page
                return redirect('index')
            
            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
            )

            messages.success(request, "Your account has been created successfully. You can now log in.")
            # login page
            return redirect('index')
        else:
            # register page
            return render(request, '404.html', {'detail': str(e)}, status=500)            
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@login_required
def logout_user(request):
    try:
        logout(request)
        messages.success(request, "You are now logged out. Come back soon!")
        # login page
        return redirect('index')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@require_http_methods(["GET"])
@login_required
def profile(request):
    try:
        addresses = Address.objects.filter(user=request.user)
        addresses_list = AddressSerializer(addresses, many=True).data
        reviews = list(mongodb.database['reviews'].find({"user_id": request.user.id}))
        total_spend, orders = get_orders(request)

        context = {
            'addresses': addresses_list,
            'orders': orders,
            'total_spend': total_spend,
            'reviews_count': len(reviews)
        }

        return render(request, 'profile.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_profile(request):
    try:
        data = request.POST

        request.user.first_name = data.get('first_name', request.user.first_name)
        request.user.last_name = data.get('last_name', request.user.last_name)
        request.user.phone = data.get('phone', request.user.phone)
        
        request.user.save()
        
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('profile')

    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@login_required
@require_http_methods(["POST"])
def change_password(request):
    try:
        data = request.POST

        current_password = data.get('old_password')
        new_password1 = data.get('new_password1')
        new_password2 = data.POST.get('new_password2')

        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('profile')

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('profile')

        request.user.set_password(new_password1)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, "Your password has been changed successfully!")
        return redirect('profile')

    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)        


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_address(request):
    try:
        data = request.POST

        print(data)
        address = Address.objects.create(
            user = request.user, 
            name = data.get('name'),
            address = data.get('address'),
            city = data.get('city'),
            state = data.get('state'),
            country = data.get('country'),
            postal_code = data.get('postal_code'),
            is_default = True if data.get('is_default') == "on" else False,
        )
        
        messages.success(request, "Your new address has been added successfully!")
        return redirect('profile')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)        



@require_POST
@login_required
def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
        address.delete()
        
        messages.success(request, "Address deleted successfully.")
        return redirect('profile')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)        


# not compelete

def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False)

def error_response(message, status=400):
    return JsonResponse({'error': message}, status=status)


@csrf_exempt
@require_http_methods(["POST"])
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