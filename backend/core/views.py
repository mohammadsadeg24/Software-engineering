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
            data = request.POST
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {username}")
                return redirect('index')
                
            else:
                messages.success(request, "Invalid username or password. Please try again.")
                return redirect('login')
        else:
            return render(request, 'login.html')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@csrf_exempt
@require_http_methods(["GET", "POST"])
def register_user(request):
    try:
        if request.method == "POST":
            data = request.POST
            
            print(data)
            if User.objects.filter(username=data.get('username')).exists() or \
            User.objects.filter(email=data.get('email')).exists():
                messages.error(request, "Username or email already exists.")
                return redirect('register')

            if data.get('password1') != data.get('password2'):
                messages.error(request, "Password and Confirm Password do not match.")
                return redirect('register')
            
            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password1'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
            )

            messages.success(request, "Your account has been created successfully. You can now log in.")
            return render(request, 'login.html')
        else:
            return render(request, 'register.html')
    except Exception as e:
        messages.error(request, str(e))
        return render(request, '404.html', {'detail': str(e)}, status=500)            


@login_required
@login_required(login_url='login')
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
@login_required(login_url='login')
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


@login_required(login_url='login')
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


@require_http_methods(["POST"])
@login_required(login_url='login')
def change_password(request):
    try:
        data = request.POST

        current_password = data.get('old_password')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')

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
@login_required(login_url='login')
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


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def update_address(request, address_id):
    ...


@require_http_methods(["GET"])
@login_required(login_url='login')
def get_addresses(request):
    ...