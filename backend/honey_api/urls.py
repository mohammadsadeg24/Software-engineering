from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),

    path('categories/', views.category_list, name='category_list'),
    # path('category/create/', views.create_category, name='create_category'),

    path('contact/', views.contact, name='contact'),

    path('products/', views.product_list, name='product_list'),
    path('product/add_review/', views.add_review, name='add_review'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/remove/<str:slug>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.get_orders, name='orders'),
    path('order/create/', views.create_order, name='create_order'),
]