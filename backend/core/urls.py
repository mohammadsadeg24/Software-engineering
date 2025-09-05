
from django.urls import path
from . import views

urlpatterns = [

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Profile
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Addresses
    path('addresses/', views.get_addresses, name='get_addresses'),
    path('addresses/create/', views.create_address, name='create_address'),
    path('addresses/<int:address_id>/update/', views.update_address, name='update_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address')
]
