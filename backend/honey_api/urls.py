from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),

    path('categories/', views.category_list, name='category_list'),
    path('category/create/', views.create_category, name='create_category'),

    path('contact/', views.contact_view, name='contact'),

    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<str:product_id>/reviews/', views.product_reviews, name='product_reviews'),

    path('cart/', views.cart_view, name='cart'),
    path('api/cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('orders/create/', views.create_order, name='create_order'),
    path('orders/', views.get_orders, name='get_orders'),
    path('orders/<str:order_id>/', views.get_order_detail, name='get_order_detail'),
]