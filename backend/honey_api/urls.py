from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
urlpatterns = [
    # -------------------------
    # Home / Categories
    # -------------------------
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.create_category, name='create_category'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # -------------------------
    # Profile / User
    # -------------------------
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # -------------------------
    # Test
    # -------------------------
    path('test-mongodb/', views.test_mongodb, name='test_mongodb'),

    # -------------------------
    # Contact
    # -------------------------
    path('contact/', views.contact_view, name='contact'),

    # -------------------------
    # Products
    # -------------------------
    path('products/', views.product_list, name='product_list'),
    path('product/<str:product_id>/reviews/', views.product_reviews, name='product_reviews'),

    # -------------------------
    # Cart
    # -------------------------
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # -------------------------
    # Orders
    # -------------------------
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/', views.get_orders, name='get_orders'),
    path('orders/<str:order_id>/', views.get_order_detail, name='get_order_detail'),
]