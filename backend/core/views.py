from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from core.models import User, Address
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
            phone=data.get('phone', ''),
            role=data.get('role', 'member')
        )
        
        return json_response({
            "success": True,
            # "product_id": product_id,
            "message": "Product created successfully"
        })
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
            "phone": request.user.phone,
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
        request.user.phone = data.get('phone', request.user.phone)
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