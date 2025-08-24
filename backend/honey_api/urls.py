# honey_api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # User Profile
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Addresses
    path('addresses/', views.get_addresses, name='get_addresses'),
    path('addresses/create/', views.create_address, name='create_address'),
    path('addresses/<int:address_id>/update/', views.update_address, name='update_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<str:slug>/', views.category_detail, name='category_detail'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<str:slug>/', views.product_detail, name='product_detail'),
    
    # Reviews
    path('reviews/create/', views.create_review, name='create_review'),
    path('products/<str:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
    # Cart
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Orders
    path('orders/', views.get_orders, name='get_orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<str:order_id>/', views.get_order_detail, name='get_order_detail'),
]

# Main project urls.py
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('honey_api.urls')),
    # Add path for serving your frontend if needed
    # path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""